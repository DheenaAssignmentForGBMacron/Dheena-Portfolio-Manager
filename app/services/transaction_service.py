"""
Transaction Service

Application service responsible for:

- Validating transaction input.
- Delegating transaction persistence to the repository.
- Invalidating the portfolio cache after mutations.

This service contains transaction business rules but no
database or Flask-specific logic.
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


# =====================================================
# Transaction Types
# =====================================================

VALID_TRANSACTION_TYPES = {
    "BUY",
    "SELL",
    "DIVIDEND",
    "BONUS",
}


# =====================================================
# Validation Helpers
# =====================================================

def _validate_transaction_type(transaction_type):
    """Validate that the transaction type is supported."""

    if transaction_type not in VALID_TRANSACTION_TYPES:
        raise ValueError(
            f"Unsupported transaction type: {transaction_type}"
        )


def _validate_brokerage(brokerage):
    """Validate common brokerage rules."""

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
    """Validate BUY and SELL transaction fields."""

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
    """Validate DIVIDEND transaction fields."""

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
    """Validate BONUS transaction fields."""

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
    """Validate transaction date format."""

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
    """
    Validate a transaction according to its transaction type.

    The service validates the transaction before it reaches
    the repository, ensuring invalid data is never persisted.
    """

    _validate_transaction_type(
        transaction_type
    )

    _validate_brokerage(
        brokerage
    )

    if transaction_type in {"BUY", "SELL"}:

        _validate_trade_transaction(
            quantity=quantity,
            price=price,
            dividend=dividend,
            bonus=bonus,
        )

    elif transaction_type == "DIVIDEND":

        _validate_dividend_transaction(
            quantity=quantity,
            price=price,
            dividend=dividend,
            bonus=bonus,
        )

    elif transaction_type == "BONUS":

        _validate_bonus_transaction(
            quantity=quantity,
            price=price,
            dividend=dividend,
            bonus=bonus,
        )

    _validate_transaction_date(
        transaction_date
    )


# =====================================================
# Create
# =====================================================

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
    """
    Validate and create a transaction.

    Portfolio cache is invalidated after a successful
    repository mutation.
    """

    _validate_transaction(
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        brokerage=brokerage,
        dividend=dividend,
        bonus=bonus,
        transaction_date=transaction_date,
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


# =====================================================
# Read
# =====================================================

def get_transactions():
    """Return all transactions."""

    return repo_get_transactions()


def get_transaction(transaction_id):
    """Return a transaction by ID."""

    return repo_get_transaction(
        transaction_id
    )


def get_asset_transactions(asset_id):
    """Return all transactions for an asset."""

    return repo_get_asset_transactions(
        asset_id
    )


# =====================================================
# Update
# =====================================================

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
    """
    Validate and update a transaction.

    Portfolio cache is invalidated after a successful
    repository mutation.
    """

    _validate_transaction(
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        brokerage=brokerage,
        dividend=dividend,
        bonus=bonus,
        transaction_date=transaction_date,
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

    invalidate_portfolio()

    return result


# =====================================================
# Delete
# =====================================================

def delete_transaction(transaction_id):
    """
    Delete a transaction and invalidate the portfolio cache.
    """

    result = repo_delete_transaction(
        transaction_id
    )

    invalidate_portfolio()

    return result