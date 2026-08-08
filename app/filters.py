from datetime import date, datetime


def currency(value):
    """Format a numeric value as Indian Rupees."""
    if value is None:
        return "₹0.00"

    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


def format_date(value):
    """Format date/datetime values as DD-MM-YYYY."""

    if value is None or value == "":
        return "-"

    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y")

    if isinstance(value, date):
        return value.strftime("%d-%m-%Y")

    if isinstance(value, str):
        # Try common database/date formats.
        for fmt in (
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        ):
            try:
                parsed = datetime.strptime(value, fmt)
                return parsed.strftime("%d-%m-%Y")
            except ValueError:
                continue

    # Don't crash the page if an unexpected value reaches the template.
    return str(value)