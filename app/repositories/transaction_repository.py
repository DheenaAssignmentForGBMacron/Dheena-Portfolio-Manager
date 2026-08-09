from app.database import get_connection


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

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO transactions
        (
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
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
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
        ),
    )

    conn.commit()
    conn.close()


# =====================================================
# Read
# =====================================================

def get_transactions():

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            t.*,
            a.name AS asset_name,
            a.symbol
        FROM transactions t
        LEFT JOIN assets a
            ON t.asset_id = a.id
        ORDER BY
            t.transaction_date DESC,
            t.id DESC
        """
    ).fetchall()

    conn.close()

    return rows


def get_transaction(transaction_id):

    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM transactions
        WHERE id = ?
        """,
        (transaction_id,),
    ).fetchone()

    conn.close()

    return row


def get_asset_transactions(asset_id):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            t.*,
            a.name AS asset_name,
            a.symbol
        FROM transactions t
        JOIN assets a
            ON t.asset_id = a.id
        WHERE t.asset_id = ?
        ORDER BY
            t.transaction_date DESC,
            t.id DESC
        """,
        (asset_id,),
    ).fetchall()

    conn.close()

    return rows


# =====================================================
# Portfolio Engine Query
# =====================================================

def get_transactions_with_assets():

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            t.*,
            a.symbol,
            a.name,
            a.asset_class
        FROM transactions t
        JOIN assets a
            ON t.asset_id = a.id
        ORDER BY
            t.transaction_date,
            t.id
        """
    ).fetchall()

    conn.close()

    return rows


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

    conn = get_connection()

    conn.execute(
        """
        UPDATE transactions
        SET
            asset = ?,
            asset_type = ?,
            asset_id = ?,
            transaction_type = ?,
            quantity = ?,
            price = ?,
            brokerage = ?,
            dividend = ?,
            bonus = ?,
            transaction_date = ?,
            notes = ?
        WHERE id = ?
        """,
        (
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
            transaction_id,
        ),
    )

    conn.commit()
    conn.close()


# =====================================================
# Delete
# =====================================================

def delete_transaction(transaction_id):

    conn = get_connection()

    conn.execute(
        """
        DELETE
        FROM transactions
        WHERE id = ?
        """,
        (transaction_id,),
    )

    conn.commit()
    conn.close()