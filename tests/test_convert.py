import csv
import subprocess
import sys
from pathlib import Path

import pytest

from shopify_supplier_csv_cleaner import convert

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def test_mapping_and_example(tmp_path):
    output = tmp_path / "shopify.csv"
    assert convert(EXAMPLES / "supplier.csv", output, title="Product", sku="Item code", price="Unit price", barcode="EAN") == 2
    assert output.read_bytes() == (EXAMPLES / "shopify.csv").read_bytes()
    rows = list(csv.DictReader(output.open()))
    assert rows[0]["Variant SKU"] == "00042"
    assert rows[0]["Variant Barcode"] == "0001234567890"
    assert rows[0]["Status"] == "draft"


def test_optional_barcode_bom_and_quoted_title(tmp_path):
    source, output = tmp_path / "source.csv", tmp_path / "shopify.csv"
    source.write_text('\ufeffTitle,SKU,Price\n"Sample, item",00001,0.5\n', encoding="utf-8")
    convert(source, output)
    row = next(csv.DictReader(output.open()))
    assert row["Title"] == "Sample, item"
    assert row["Variant Barcode"] == ""
    assert row["Variant Price"] == "0.50"


@pytest.mark.parametrize("body", [
    "Sample,0001,12.345\n", "Sample,0001,NaN\n", 'Sample,0001,"12,50"\n',
    "Sample,0001,-1.00\n", "Sample,0001,1.00\nSample,0001,1.00\n",
    "Sample,0001,1.00\nOther,0001,2.00\n", "Sample, 0001,1.00\n",
    "=1+1,0001,1.00\n", "Sample,0001,1.00,extra\n", "Sample,0001\n",
    "Sample,0001,1.00\n\n", "Sample,,1.00\n", "Sample\x00,0001,1.00\n",
    "Sample,code.a,1.00\nSample,code-a,1.00\n",
])
def test_invalid_rows_block_all_export(tmp_path, body):
    source, output = tmp_path / "source.csv", tmp_path / "shopify.csv"
    source.write_text("Title,SKU,Price\n" + body)
    with pytest.raises((ValueError, csv.Error)):
        convert(source, output)
    assert not output.exists()


@pytest.mark.parametrize("text", ["Title,SKU,Price\n", "Title,SKU,SKU\nSample,001,1\n", "Wrong,SKU,Price\nSample,001,1\n"])
def test_bad_headers_or_empty_file(tmp_path, text):
    source = tmp_path / "source.csv"
    source.write_text(text)
    with pytest.raises(ValueError):
        convert(source, tmp_path / "shopify.csv")


def test_overwrite_and_bad_mapping(tmp_path):
    source, output = tmp_path / "source.csv", tmp_path / "shopify.csv"
    source.write_text("Title,SKU,Price\nSample,0001,1.00\n")
    output.write_text("keep")
    with pytest.raises(FileExistsError):
        convert(source, output)
    assert output.read_text() == "keep"
    with pytest.raises(ValueError):
        convert(source, output, title="SKU")


def test_cli(tmp_path):
    output = tmp_path / "shopify.csv"
    result = subprocess.run([sys.executable, "-m", "shopify_supplier_csv_cleaner", str(EXAMPLES / "supplier.csv"), str(output), "--title", "Product", "--sku", "Item code", "--price", "Unit price", "--barcode", "EAN"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    failed = subprocess.run([sys.executable, "-m", "shopify_supplier_csv_cleaner", str(EXAMPLES / "supplier.csv"), str(output)], capture_output=True, text=True)
    assert failed.returncode == 2
    assert "Traceback" not in failed.stderr
