# shopify-supplier-csv-cleaner

Map supplier CSV columns to new Shopify draft products while preserving existing SKU and barcode leading zeros.

## Install

Python 3.10 or newer. From this repository:

```sh
python -m venv .venv
# Activate .venv using your shell's activation command, then:
python -m pip install .
```

No runtime dependencies beyond Python’s standard library. You can also run directly from the repository after installing its dependencies.

## Usage

```sh
python -m shopify_supplier_csv_cleaner examples/supplier.csv shopify.csv \
  --title Product --sku "Item code" --price "Unit price" --barcode EAN
```

The output path must be new. Existing files are never overwritten. All conversion runs locally; the CLI makes no network requests. Conversion/validation errors exit with code 2. Run `python -m shopify_supplier_csv_cleaner --help` for arguments.

Importable API (returns the number of exported rows):

```python
from shopify_supplier_csv_cleaner import convert

convert("examples/supplier.csv", "shopify.csv",
        title="Product", sku="Item code", price="Unit price", barcode="EAN")
```

Files under `examples/` are entirely fictional. Expected output:

```csv
Handle,Title,Option1 Name,Option1 Value,Variant SKU,Variant Price,Variant Barcode,Status
sample-notebook-00042,Sample notebook,Title,Default Title,00042,12.50,0001234567890,draft
sample-pen-00043,Sample pen,Title,Default Title,00043,2.00,0001234567891,draft
```

## Capabilities and limits

- UTF-8 (optional BOM), comma-separated CSV only. Header names are case-sensitive and must be unique. Every row must have the header's column count; blank data rows cause an error. Unmapped columns are ignored.
- Default mapped headers: `Title`, `SKU`, `Price`; Barcode is omitted unless `--barcode` is provided. Each mapping must select a distinct source column.
- Prices must be nonnegative dot-decimal values with at most two decimal places, no separators, currency symbols or surrounding whitespace. The output normalizes prices to two decimals; it does not convert currencies or European decimals.
- SKU and Barcode stay strings: existing zeros are preserved, missing zeros cannot be recovered. Surrounding identifier whitespace, empty titles/SKUs, control characters and formula-leading mapped text are rejected. Titles have surrounding whitespace trimmed.
- Generates ASCII handles from title and SKU. Repeated SKUs (including identical rows), handle collisions and invalid rows stop the entire export. There is no duplicate merge, conflict review, partial export or issue-list report.
- One default variant per product, `draft` status only. No images, size/color variants, inventory, existing-product updates, store comparison or synchronization. Review the Shopify import yourself; this tool does not connect to a store. This independent project is not affiliated with, endorsed by or sponsored by Shopify. Shopify is a trademark of its respective owner.
- CSV has no column types: Excel or another spreadsheet can strip zeros when opening or saving it. Import SKU and Barcode as text, or import the generated file directly into Shopify.

## This CLI vs Online version

| Feature | This CLI | Online version |
| --- | --- | --- |
| Column mapping and identifier zeros | Yes | Yes |
| Input | UTF-8 comma CSV | UTF-8 or Windows-1252; comma or semicolon CSV |
| European decimal prices | No | Explicit conversion to dot decimals; no currency conversion |
| Identical rows / duplicate conflicts | Stops on repeated SKUs | Merge identical valid rows; review conflicts, optional keep-first |
| Preview and validation | CLI errors; no preview | Checked preview, issue list, valid-row export and skipped-row list |
| Compare existing products | No | Compare with an uploaded Shopify export; no live store connection |
| Output | New single-variant draft CSV | New single-variant draft CSV |

## Online version

[Rowmoss online](https://rowmoss.pivlu.com/?utm_source=github&utm_medium=readme&utm_campaign=shopify-supplier-csv-cleaner) is a separate online version by the same author, Zijian Xiao. The online version needs no local installation and includes a preview to check mappings, prices, identifiers and issues before delivery. Its store comparison uses an uploaded Shopify product export, not a live store connection. It also supports supplier row tags; it does not support inventory, variants or existing-product updates.

Current online free allowance (available now; product information dated November 10, 2026):

Your first 3 complete converted files per browser credential are free, with up to 100 source product rows each. No registration or payment card is required for this browser allowance.

3 complete converted files per browser credential without registration, plus 3 per account; anonymous and account use together is capped at 6 free complete deliveries per network address in 30 days; up to 100 source product rows per free file, with all conversion features including supplier row tags, store comparison and the skipped-row list. Before a successful complete download, previews show 20 rows and 20 issues. A successful free download allows viewing all rows up to 100. Larger files or exhausted allowances show upgrade options.

The local MIT-licensed CLI has no online quota. Visiting the link is optional; uploaded online files are processed by the online service.

## Tests

```sh
python -m pip install ".[test]"
python -m pytest
```

## License

MIT. Copyright (c) 2026 Zijian Xiao. See [LICENSE](LICENSE).
