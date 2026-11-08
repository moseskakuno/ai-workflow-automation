
from pypdf import PdfReader
from io import BytesIO

from validators import validate_invoice
from ai_processor import extract_invoice_data


def process_invoice(uploaded_file):
    """
    Processes an uploaded PDF invoice:
    1. Extracts text from PDF
    2. Uses AI to extract invoice data
    3. Validates the extracted data
    """

    # Read PDF
    pdf_reader = PdfReader(BytesIO(uploaded_file.read()))

    invoice_text = ""

    for page in pdf_reader.pages:
        invoice_text += page.extract_text() or ""

    if not invoice_text.strip():
        raise ValueError(
            "No readable text found in this PDF. "
            "Scanned invoices require OCR."
        )

    # Extract structured data using AI
    invoice_data = extract_invoice_data(invoice_text)

    # Validate extracted data
    validation_result = validate_invoice(invoice_data)

    return {
        "invoice_data": invoice_data,
        "validation": validation_result,
    }
