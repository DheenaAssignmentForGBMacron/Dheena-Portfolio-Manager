"""
Transaction Service

Application service responsible for:

- Validating transaction input.
- Delegating persistence to the repository.
- Invalidating portfolio state after successful mutations.

This layer owns transaction business rules.
It contains no Flask or database implementation details.
"""

from datetime import datetime

from app.repositories.transaction_repository import (
    add_transaction as repo_add_transaction,
    get_transactions as repo_get_transactions,
    get_transaction as repo_get_transaction,
    get_asset_transactions as repo_get_asset_transactions,
    update_transaction as repo_update_transaction,
    delete_transaction as repo_delete_transaction,
)

from app.services.portfolio_service import invalidate_portfolio


VALID_TRANSACTION_TYPES = frozenset({
    "BUY",
    "SELL",
    "DIVIDEND",
    "BONUS",
})


def _validate_transaction_type(transaction_type):
    """Validate transaction type."""

    if transaction_type not in VALID_TRANSACTION_TYPES:
        raise ValueError(
            f"Unsupported transaction type: {transaction_type}"
        )


def _validate_numeric(value, field_name):
    """Ensure a financial input is numeric."""

    if value is None:
        raise ValueError(
            f"{field_name} is required."
        )

    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{field_name} must be numeric."
        )


def _validate_brokerage(brokerage):
    """Validate brokerage."""

    brokerage = _validate_numeric(
        brokerage,
        "Brokerage",
    )

    if brokerage < 0:
        raise ValueError(
            "Brokerage cannot be negative."
        )


def _validate_trade_transaction(
    quantity,
    price,
    dividend,
    bonus,
):
    """Validate BUY and SELL transactions."""

    quantity = _validate_numeric(
        quantity,
        "Quantity",
    )

    price = _validate_numeric(
        price,
        "Price",
    )

    dividend = _validate_numeric(
        dividend,
        "Dividend",
    )

    bonus = _validate_numeric(
        bonus,
        "Bonus",
    )

    if quantity <= 0:
        raise ValueError(
            "Quantity must be greater than zero."
        )

    if price < 0:
        raise ValueError(
            "Price cannot be negative."
        )

    if dividend != 0:
        raise ValueError(
            "BUY/SELL transactions cannot contain dividends."
        )

    if bonus != 0:
        raise ValueError(
            "BUY/SELL transactions cannot contain bonus shares."
        )


def _validate_dividend_transaction(
    quantity,
    price,
    dividend,
    bonus,
):
    """Validate DIVIDEND transactions."""

    quantity = _validate_numeric(
        quantity,
        "Quantity",
    )

    price = _validate_numeric(
        price,
        "Price",
    )

    dividend = _validate_numeric(
        dividend,
        "Dividend",
    )

    bonus = _validate_numeric(
        bonus,
        "Bonus",
    )

    if dividend <= 0:
        raise ValueError(
            "Dividend amount must be greater than zero."
        )

    if quantity != 0:
        raise ValueError(
            "Dividend transactions cannot contain quantity."
        )

    if price != 0:
        raise ValueError(
            "Dividend transactions cannot contain price."
        )

    if bonus != 0:
        raise ValueError(
            "Dividend transactions cannot contain bonus shares."
        )


def _validate_bonus_transaction(
    quantity,
    price,
    dividend,
    bonus,
):
    """Validate BONUS transactions."""

    quantity = _validate_numeric(
        quantity,
        "Quantity",
    )

    price = _validate_numeric(
        price,
        "Price",
    )

    dividend = _validate_numeric(
        dividend,
        "Dividend",
    )

    bonus = _validate_numeric(
        bonus,
        "Bonus",
    )

    if bonus <= 0:
        raise ValueError(
            "Bonus quantity must be greater than zero."
        )

    if quantity != 0:
        raise ValueError(
            "Bonus transactions cannot contain quantity."
        )

    if price != 0:
        raise ValueError(
            "Bonus transactions cannot contain price."
        )

    if dividend != 0:
        raise ValueError(
            "Bonus transactions cannot contain dividends."
        )


def _validate_transaction_date(transaction_date):
    """Validate YYYY-MM-DD transaction date."""

    try:
        datetime.strptime(
            transaction_date,
            "%Y-%m-%d",
        )
    except (TypeError, ValueError):
        raise ValueError(
            "Transaction date must be a valid date in YYYY-MM-DD format."
        )


def _validate_transaction(
    transaction_type,
    quantity,
    price,
    brokerage,
    dividend,
    bonus,
    transaction_date,
):
    """Validate a transaction according to its type."""

    _validate_transaction_type(
        transaction_type
    )

    _validate_brokerage(
        brokerage
    )

    if transaction_type in {"BUY", "SELL"}:
        _validate_trade_transaction(
            quantity,
            price,
            dividend,
            bonus,
        )

    elif transaction_type == "DIVIDEND":
        _validate_dividend_transaction(
            quantity,
            price,
            dividend,
            bonus,
        )

    elif transaction_type == "BONUS":
        _validate_bonus_transaction(
            quantity,
            price,
            dividend,
            bonus,
        )

    _validate_transaction_date(
        transaction_date
    )


def add_transaction(
    asset,
    asset_type,
    asset_id,
    transaction_type,
    quantity,
    price,
    brokerage,
    dividend,
    bonus,
    transaction_date,
    notes,
):
    """Validate and create a transaction."""

    _validate_transaction(
        transaction_type,
        quantity,
        price,
        brokerage,
        dividend,
        bonus,
        transaction_date,
    )

    result = repo_add_transaction(
        asset,
        asset_type,
        asset_id,
        transaction_type,
        quantity,
        price,
        brokerage,
        dividend,
        bonus,
        transaction_date,
        notes,
    )

    invalidate_portfolio()

    return result


def get_transactions():
    """Return all transactions."""

    return repo_get_transactions()


def get_transaction(transaction_id):
    """Return a transaction by ID."""

    return repo_get_transaction(
        transaction_id
    )


def get_asset_transactions(asset_id):
    """Return transactions belonging to an asset."""

    return repo_get_asset_transactions(
        asset_id
    )


def update_transaction(
    transaction_id,
    asset,
    asset_type,
    asset_id,
    transaction_type,
    quantity,
    price,
    brokerage,
    dividend,
    bonus,
    transaction_date,
    notes,
):
    """Validate and update a transaction."""

    _validate_transaction(
        transaction_type,
        quantity,
        price,
        brokerage,
        dividend,
        bonus,
        transaction_date,
    )

    result = repo_update_transaction(
        transaction_id,
        asset,
        asset_type,
        asset_id,
        transaction_type,
        quantity,
        price,
        brokerage,
        dividend,
        bonus,
        transaction_date,
        notes,
    )

    if result:
        invalidate_portfolio()

    return result


def delete_transaction(transaction_id):
    """Delete a transaction."""

    result = repo_delete_transaction(
        transaction_id
    )

    if result:
        invalidate_portfolio()

    return result