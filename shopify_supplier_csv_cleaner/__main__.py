"""Command-line entry point."""
import argparse
import csv
import sys
from . import convert


def main():
    parser = argparse.ArgumentParser(description='Map supplier CSV columns to Shopify draft products while preserving SKU and barcode leading zeros.')
    parser.add_argument("input")
    parser.add_argument("output", help="New output path; existing files are never overwritten")
    parser.add_argument("--title", default="Title", help="Source title column")
    parser.add_argument("--sku", default="SKU", help="Source SKU column")
    parser.add_argument("--price", default="Price", help="Source price column")
    parser.add_argument("--barcode", help="Optional source barcode column")
    args = parser.parse_args()
    try:
        count = convert(args.input, args.output, title=args.title, sku=args.sku, price=args.price, barcode=args.barcode)
    except (ValueError, OSError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {count} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
