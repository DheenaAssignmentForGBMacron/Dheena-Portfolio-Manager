from app.repositories.transaction_repository import (
    add_transaction as repo_add_transaction,
    get_transactions as repo_get_transactions,
    get_transaction as repo_get_transaction,
    get_asset_transactions as repo_get_asset_transactions,
    update_transaction as repo_update_transaction,
    delete_transaction as repo_delete_transaction,
)

from app.services.portfolio_service import invalidate_portfolio

from datetime import datetime

VALID_TRANSACTION_TYPES = {"BUY", "SELL"}

def _validate_transaction(
    transaction_type,
    quantity,
    price,
    brokerage,
    transaction_date,
):
    if transaction_type not in VALID_TRANSACTION_TYPES:
        raise ValueError(
            f"Unsupported transaction type: {transaction_type}"
        )

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    if price < 0:
        raise ValueError("Price cannot be negative.")

    if brokerage < 0:
        raise ValueError("Brokerage cannot be negative.")

    try:
        datetime.strptime(transaction_date, "%Y-%m-%d")
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
    transaction_date,
    notes,
):
    _validate_transaction(
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        brokerage=brokerage,
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
    transaction_date,
    notes,
):
    _validate_transaction(
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        brokerage=brokerage,
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

    result = repo_delete_transaction(transaction_id)

    # Transaction data changed.
    # Cached portfolio is now stale.
    invalidate_portfolio()

    return result