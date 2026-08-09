from datetime import date

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.services.asset_service import get_asset
from app.services.portfolio_service import get_holding

from app.services.transaction_service import (
    add_transaction,
    delete_transaction,
    get_transaction,
    get_transactions,
    update_transaction,
)


transaction_bp = Blueprint("transaction", __name__)


# ---------------------------------
# Transactions
# ---------------------------------

@transaction_bp.route("/transactions")
def transactions():

    transactions = get_transactions()

    return render_template(
        "transactions.html",
        transactions=transactions,
    )


# ---------------------------------
# Add Transaction
# ---------------------------------

@transaction_bp.route("/add-transaction", methods=["GET", "POST"])
def add_transaction_page():

    if request.method == "GET":

        return render_template(
            "add_transaction.html",
            today=date.today().isoformat(),
        )

    asset_id = request.form["asset_id"]

    # ---------------------------------
    # Validate Asset
    # ---------------------------------

    if not asset_id:

        return render_template(
            "add_transaction.html",
            today=date.today().isoformat(),
            error_message=(
                "Please select a valid asset from the search results "
                "or create a new asset first."
            ),
        )

    try:
        asset_id = int(asset_id)
    except ValueError:

        return render_template(
            "add_transaction.html",
            today=date.today().isoformat(),
            error_message="Invalid asset selected.",
        )

    asset_record = get_asset(asset_id)

    if asset_record is None:

        return render_template(
            "add_transaction.html",
            today=date.today().isoformat(),
            error_message="Selected asset does not exist.",
        )

    # ---------------------------------
    # Derive Asset Metadata
    # ---------------------------------

    asset = asset_record["symbol"]
    asset_type = asset_record["asset_class"]

    transaction_type = request.form["transaction_type"]

    quantity = float(request.form["quantity"])
    price = float(request.form["price"])
    brokerage = float(request.form["brokerage"] or 0)

    transaction_date = request.form["transaction_date"]
    notes = request.form["notes"]

    # ---------------------------------
    # Validate SELL quantity
    # ---------------------------------

    if transaction_type == "SELL":

        holding = get_holding(asset_id)

        current_qty = holding.qty if holding else 0

        if quantity > current_qty:

            return render_template(
                "add_transaction.html",
                today=date.today().isoformat(),
                error_message=(
                    f"Cannot sell {quantity:g} units. "
                    f"Current holding is only {current_qty:g}."
                ),
            )

    add_transaction(
        asset=asset,
        asset_type=asset_type,
        asset_id=asset_id,
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        brokerage=brokerage,
        transaction_date=transaction_date,
        notes=notes,
    )

    flash(
        "Transaction added successfully.",
        "success",
    )

    return redirect(url_for("portfolio.portfolio"))


# ---------------------------------
# Edit Transaction
# ---------------------------------

@transaction_bp.route(
    "/edit-transaction/<int:transaction_id>",
    methods=["GET", "POST"],
)
def edit_transaction_page(transaction_id):

    tx = get_transaction(transaction_id)

    if tx is None:
        return "Transaction not found", 404

    if request.method == "GET":

        return render_template(
            "edit_transaction.html",
            tx=tx,
            today=date.today().isoformat(),
        )

    asset_id = request.form["asset_id"]

    try:
        asset_id = int(asset_id)
    except ValueError:

        return render_template(
            "edit_transaction.html",
            tx=tx,
            today=date.today().isoformat(),
            error_message="Invalid asset selected.",
        )

    asset_record = get_asset(asset_id)

    if asset_record is None:

        return render_template(
            "edit_transaction.html",
            tx=tx,
            today=date.today().isoformat(),
            error_message="Selected asset does not exist.",
        )

    # ---------------------------------
    # Derive Asset Metadata
    # ---------------------------------

    asset = asset_record["symbol"]
    asset_type = asset_record["asset_class"]

    update_transaction(
        transaction_id=transaction_id,
        asset=asset,
        asset_type=asset_type,
        asset_id=asset_id,
        transaction_type=request.form["transaction_type"],
        quantity=float(request.form["quantity"]),
        price=float(request.form["price"]),
        brokerage=float(
            request.form.get("brokerage", 0) or 0
        ),
        transaction_date=request.form["transaction_date"],
        notes=request.form["notes"],
    )

    flash(
        "Transaction updated successfully.",
        "success",
    )

    return redirect(url_for("transaction.transactions"))


# ---------------------------------
# Delete Transaction
# ---------------------------------

@transaction_bp.route(
    "/delete-transaction/<int:transaction_id>"
)
def remove_transaction(transaction_id):

    delete_transaction(transaction_id)

    flash(
        "Transaction deleted successfully.",
        "success",
    )

    return redirect(url_for("transaction.transactions"))