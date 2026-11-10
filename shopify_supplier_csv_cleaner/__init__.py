"""Map supplier columns into new, single-variant Shopify draft products."""
import csv
import io
import re
import unicodedata
from decimal import Decimal
from pathlib import Path

__all__ = ["convert"]
HEADERS = ["Handle", "Title", "Option1 Name", "Option1 Value", "Variant SKU", "Variant Price", "Variant Barcode", "Status"]


def _slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def convert(source, target, *, title="Title", sku="SKU", price="Price", barcode=None):
    """Map UTF-8 comma CSV into a new Shopify CSV; return product count.

    Column arguments are exact source header names. Barcode is optional.
    """
    source, target = Path(source), Path(target)
    if source.suffix.lower() != ".csv" or target.suffix.lower() != ".csv":
        raise ValueError("Use .csv input and output paths.")
    mapping = [title, sku, price] + ([barcode] if barcode is not None else [])
    if any(not value for value in mapping) or len(set(mapping)) != len(mapping):
        raise ValueError("Map distinct, nonempty column names.")
    rows, skus, handles = [], set(), set()
    with source.open(encoding="utf-8-sig", newline="") as input_file:
        reader = csv.reader(input_file, strict=True)
        headers = next(reader, [])
        if len(set(headers)) != len(headers) or any(value not in headers for value in mapping):
            raise ValueError("Require unique headers and all mapped columns.")
        positions = [headers.index(value) for value in mapping]
        for number, cells in enumerate(reader, 2):
            if len(cells) != len(headers):
                raise ValueError(f"Row {number}: column count differs from header.")
            values = [cells[index] for index in positions]
            if any(value.lstrip().startswith(("=", "+", "-", "@")) or
                   any(unicodedata.category(ch).startswith("C") for ch in value) for value in values):
                raise ValueError(f"Row {number}: formula-leading text or control character.")
            name, code, cost = values[:3]
            bar = values[3] if barcode is not None else ""
            if not name.strip() or not code.strip() or code != code.strip() or bar != bar.strip():
                raise ValueError(f"Row {number}: require title, SKU and identifiers without surrounding whitespace.")
            if not re.fullmatch(r"\d{1,13}(?:\.\d{1,2})?", cost):
                raise ValueError(f"Row {number}: price must be nonnegative dot-decimal with at most two decimal places.")
            handle = "-".join(part for part in (_slug(name)[:60], _slug(code)) if part)
            if not handle or code in skus or handle in handles:
                raise ValueError(f"Row {number}: require unique SKUs and generated handles.")
            skus.add(code)
            handles.add(handle)
            rows.append([handle, name.strip(), "Title", "Default Title", code, format(Decimal(cost), ".2f"), bar, "draft"])
    if not rows:
        raise ValueError("No products found.")
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(HEADERS)
    writer.writerows(rows)
    with target.open("x", encoding="utf-8", newline="") as output:
        output.write(buffer.getvalue())
    return len(rows)
