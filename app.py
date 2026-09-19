from __future__ import annotations

import argparse
import json

from document_extractor import process_folder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract structured fields from a folder of PDF documents."
    )
    parser.add_argument("--input", default="data/sample_pdfs", help="Folder containing PDFs")
    parser.add_argument("--output", default="output", help="Folder for JSON/CSV results")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    results = process_folder(args.input, args.output)
    print(f"Processed {len(results)} PDF document(s).")
    for result in results:
        summary = {
            "filename": result["filename"],
            "type": result["document_type"],
            "total_due": result["fields"]["total_due"],
        }
        print(json.dumps(summary))


if __name__ == "__main__":
    main()
