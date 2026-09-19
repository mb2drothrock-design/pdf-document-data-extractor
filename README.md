# PDF Document Data Extraction Pipeline

A Python portfolio project that processes PDF documents in batches, extracts structured business data, classifies document types, and exports machine-readable JSON and CSV results.

## Features

- Batch-processes every PDF in a folder
- Extracts text using PyMuPDF
- Classifies common business documents using transparent keyword scoring
- Extracts invoice numbers, purchase order numbers, account numbers, dates, emails, phone numbers, currency amounts, and totals
- Writes one structured JSON file per document
- Produces consolidated CSV and JSON summaries
- Computes SHA-256 hashes for traceability
- Includes automated tests and fictional sample documents

## Tech stack

- Python 3.10+
- PyMuPDF
- Regular expressions
- JSON / CSV
- `unittest`

## Project structure

```text
pdf-document-data-extractor/
├── app.py
├── document_extractor/
│   ├── __init__.py
│   └── core.py
├── data/
│   └── sample_pdfs/
├── output/
│   ├── json/
│   ├── all_results.json
│   └── extraction_summary.csv
├── tests/
│   └── test_extractor.py
├── requirements.txt
└── README.md
```

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 app.py
```

Custom folders:

```bash
python3 app.py --input /path/to/pdfs --output /path/to/results
```

## Testing

```bash
python3 -m unittest discover -s tests
```

## What this demonstrates

This project demonstrates PDF processing, batch automation, text extraction, regex-based information extraction, document classification, structured data generation, file integrity hashing, validation, command-line tooling, and automated testing.

## Portfolio note

This is a self-directed portfolio project. All sample companies, documents, contacts, account numbers, and monetary values are fictional.
