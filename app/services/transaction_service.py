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
# Validation
# =====================================================

def _validate_transaction(
    transaction_type,
    quantity,
    price,
    brokerage,
    dividend,
    bonus,
    transaction_date,
):
    # -------------------------------------------------
    # Transaction Type
    # -------------------------------------------------

    if transaction_type not in VALID_TRANSACTION_TYPES:
        raise ValueError(
            f"Unsupported transaction type: {transaction_type}"
        )

    # -------------------------------------------------
    # Common Validation
    # -------------------------------------------------

    if brokerage < 0:
        raise ValueError(
            "Brokerage cannot be negative."
        )

    # -------------------------------------------------
    # BUY / SELL
    # -------------------------------------------------

    if transaction_type in {"BUY", "SELL"}:

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

    # -------------------------------------------------
    # DIVIDEND
    # -------------------------------------------------

    elif transaction_type == "DIVIDEND":

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

    # -------------------------------------------------
    # BONUS
    # -------------------------------------------------

    elif transaction_type == "BONUS":

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

    # -------------------------------------------------
    # Date
    # -------------------------------------------------

    try:

        datetime.strptime(
            transaction_date,
            "%Y-%m-%d",
        )

    except (TypeError, ValueError):

        raise ValueError(
            "Transaction date must be a valid date in YYYY-MM-DD format."
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

    # Transaction data changed.
    # Cached portfolio is now stale.

    invalidate_portfolio()

    return result


# =====================================================
# Read
# =====================================================

def get_transactions():

    return repo_get_transactions()


def get_transaction(transaction_id):

    return repo_get_transaction(transaction_id)


def get_asset_transactions(asset_id):

    return repo_get_asset_transactions(asset_id)


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

    # Transaction data changed.
    # Cached portfolio is now stale.

    invalidate_portfolio()

    return result


# =====================================================
# Delete
# =====================================================

def delete_transaction(transaction_id):

    result = repo_delete_transaction(
        transaction_id
    )

    # Transaction data changed.
    # Cached portfolio is now stale.

    invalidate_portfolio()

    return result