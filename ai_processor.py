
import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def extract_invoice_data(invoice_text: str) -> dict:
    """
    Uses AI to extract structured information from invoice text.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing in the .env file.")

    if not model:
        raise ValueError("OPENAI_MODEL is missing in the .env file.")

    if not invoice_text.strip():
        raise ValueError("The invoice contains no readable text.")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        instructions="""
        You are an invoice data extraction assistant.

        Extract the following information from the invoice:
        - vendor
        - invoice_number
        - invoice_date
        - net_amount
        - tax_amount
        - total_amount

        Return ONLY valid JSON.
        Do not invent missing information.
        Use null for fields that cannot be found.
        Amounts must be numbers, without currency symbols.

        Example:
        {
            "vendor": "Example GmbH",
            "invoice_number": "INV-2026-001",
            "invoice_date": "2026-11-08",
            "net_amount": 1000.00,
            "tax_amount": 190.00,
            "total_amount": 1190.00
        }
        """,
        input=invoice_text[:20000],
    )

    extracted_text = response.output_text

    if not extracted_text:
        raise ValueError("The AI returned an empty response.")

    try:
        invoice_data = json.loads(extracted_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The AI response was not valid JSON."
        ) from error

    return invoice_data
