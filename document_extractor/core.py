from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import fitz


DATE_PATTERN = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]\d{3}[-.\s]\d{4}(?!\d)")
MONEY_PATTERN = re.compile(r"(?<!\w)\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?")

FIELD_PATTERNS = {
    "invoice_number": [
        re.compile(r"\bInvoice\s*(?:#|No\.?|Number)\s*[:#-]?\s*([A-Z0-9-]+)", re.I),
    ],
    "purchase_order_number": [
        re.compile(r"\b(?:Purchase\s+Order|PO)\s*(?:#|No\.?|Number)\s*[:#-]?\s*([A-Z0-9-]+)", re.I),
    ],
    "account_number": [
        re.compile(r"\bAccount\s*(?:#|No\.?|Number)\s*[:#-]?\s*([A-Z0-9-]+)", re.I),
    ],
}

TOTAL_PATTERNS = [
    re.compile(r"\b(?:Total\s+Due|Amount\s+Due|Grand\s+Total)\s*[:$]?\s*(\$?\s?[0-9,]+\.\d{2})", re.I),
    re.compile(r"\bTotal\s*[:$]?\s*(\$?\s?[0-9,]+\.\d{2})", re.I),
]

DOCUMENT_TYPE_KEYWORDS = {
    "invoice": {"invoice": 4, "amount due": 3, "bill to": 2, "subtotal": 1},
    "purchase_order": {"purchase order": 4, "po number": 3, "ship to": 2, "vendor": 1},
    "contract": {"agreement": 3, "effective date": 2, "terms": 1, "party": 1, "parties": 1},
    "receipt": {"receipt": 4, "payment method": 2, "change": 1, "cashier": 1},
    "statement": {"statement": 4, "account number": 2, "balance": 2, "transactions": 1},
}


def extract_text(pdf_path: str | Path) -> tuple[str, int]:
    path = Path(pdf_path)
    with fitz.open(path) as doc:
        text = "\n".join(page.get_text("text") for page in doc)
        return text, doc.page_count


def detect_document_type(text: str) -> tuple[str, dict[str, int]]:
    lower = text.lower()
    scores: dict[str, int] = {}
    for doc_type, keywords in DOCUMENT_TYPE_KEYWORDS.items():
        score = sum(weight for keyword, weight in keywords.items() if keyword in lower)
        scores[doc_type] = score
    best_type = max(scores, key=scores.get)
    return (best_type if scores[best_type] > 0 else "unknown", scores)


def _first_match(patterns: list[re.Pattern[str]], text: str) -> str | None:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def _extract_total(text: str) -> str | None:
    for pattern in TOTAL_PATTERNS:
        match = pattern.search(text)
        if match:
            value = match.group(1).replace(" ", "")
            return value if value.startswith("$") else f"${value}"
    return None


def extract_fields(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {
        name: _first_match(patterns, text) for name, patterns in FIELD_PATTERNS.items()
    }
    fields.update(
        {
            "dates": sorted(set(DATE_PATTERN.findall(text))),
            "emails": sorted(set(EMAIL_PATTERN.findall(text))),
            "phone_numbers": sorted(set(PHONE_PATTERN.findall(text))),
            "currency_amounts": sorted(set(MONEY_PATTERN.findall(text))),
            "total_due": _extract_total(text),
        }
    )
    return fields


def extract_document(pdf_path: str | Path) -> dict[str, Any]:
    path = Path(pdf_path)
    text, page_count = extract_text(path)
    document_type, type_scores = detect_document_type(text)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    return {
        "filename": path.name,
        "page_count": page_count,
        "sha256": digest,
        "document_type": document_type,
        "document_type_scores": type_scores,
        "fields": extract_fields(text),
        "text_preview": " ".join(text.split())[:300],
    }


def process_folder(input_dir: str | Path, output_dir: str | Path) -> list[dict[str, Any]]:
    source = Path(input_dir)
    destination = Path(output_dir)
    json_dir = destination / "json"
    destination.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(source.glob("*.pdf"))
    results = [extract_document(path) for path in pdf_files]

    for result in results:
        output_path = json_dir / f"{Path(result['filename']).stem}.json"
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    csv_path = destination / "extraction_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "filename",
                "document_type",
                "page_count",
                "invoice_number",
                "purchase_order_number",
                "account_number",
                "total_due",
                "dates",
                "emails",
            ],
        )
        writer.writeheader()
        for result in results:
            fields = result["fields"]
            writer.writerow(
                {
                    "filename": result["filename"],
                    "document_type": result["document_type"],
                    "page_count": result["page_count"],
                    "invoice_number": fields["invoice_number"] or "",
                    "purchase_order_number": fields["purchase_order_number"] or "",
                    "account_number": fields["account_number"] or "",
                    "total_due": fields["total_due"] or "",
                    "dates": "; ".join(fields["dates"]),
                    "emails": "; ".join(fields["emails"]),
                }
            )

    (destination / "all_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results
