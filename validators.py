
from decimal import Decimal, InvalidOperation


def validate_invoice(invoice: dict) -> dict:
    """
    Validates extracted invoice data using business rules.
    """

    errors = []
    warnings = []

    required_fields = [
        "vendor",
        "invoice_number",
        "invoice_date",
        "net_amount",
        "tax_amount",
        "total_amount",
    ]

    # 1. Check required fields
    for field in required_fields:
        if not invoice.get(field):
            errors.append(f"Missing required field: {field}")

    # Stop further checks if required fields are missing
    if errors:
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
        }

    # 2. Convert amounts into decimal values
    try:
        net = Decimal(str(invoice["net_amount"]))
        tax = Decimal(str(invoice["tax_amount"]))
        total = Decimal(str(invoice["total_amount"]))
    except (InvalidOperation, ValueError, TypeError):
        return {
            "valid": False,
            "errors": ["Invoice amounts must be valid numbers."],
            "warnings": warnings,
        }

    # 3. Check for negative amounts
    if net < 0 or tax < 0 or total < 0:
        errors.append("Invoice amounts cannot be negative.")

    # 4. Check calculation consistency
    if abs((net + tax) - total) > Decimal("0.02"):
        errors.append("Net amount plus tax does not match total amount.")

    # 5. Check approval threshold
    if total > Decimal("5000"):
        warnings.append(
            "Invoice exceeds €5,000 and requires additional approval."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
