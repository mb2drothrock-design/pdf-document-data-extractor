import tempfile
import unittest
from pathlib import Path

from document_extractor.core import detect_document_type, extract_fields, process_folder


SAMPLE_TEXT = """
ACME DESIGN CO.
INVOICE # INV-2048
Invoice Date: 2026-09-19
Due Date: 2026-10-03
Bill To: Blue Ridge Retail
billing@acme.example
Subtotal $725.00
Tax $58.00
Total Due $783.00
"""


class ExtractorTests(unittest.TestCase):
    def test_invoice_fields(self):
        fields = extract_fields(SAMPLE_TEXT)
        self.assertEqual(fields["invoice_number"], "INV-2048")
        self.assertEqual(fields["total_due"], "$783.00")
        self.assertIn("2026-09-19", fields["dates"])
        self.assertIn("billing@acme.example", fields["emails"])

    def test_document_type(self):
        doc_type, scores = detect_document_type(SAMPLE_TEXT)
        self.assertEqual(doc_type, "invoice")
        self.assertGreater(scores["invoice"], scores["contract"])

    def test_sample_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = process_folder("data/sample_pdfs", tmp)
            self.assertEqual(len(results), 3)
            self.assertTrue((Path(tmp) / "all_results.json").exists())
            self.assertTrue((Path(tmp) / "extraction_summary.csv").exists())


if __name__ == "__main__":
    unittest.main()
