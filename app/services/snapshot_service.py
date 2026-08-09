from datetime import date

from app.database import get_connection
from app.services.portfolio_service import get_portfolio


# =====================================================
# Snapshot Utilities
# =====================================================

def snapshot_exists(snapshot_date=None):

    if snapshot_date is None:
        snapshot_date = date.today().isoformat()

    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT id
            FROM portfolio_snapshots
            WHERE snapshot_date = ?
            """,
            (snapshot_date,),
        ).fetchone()

        return row is not None

    finally:
        conn.close()


def asset_snapshot_exists(snapshot_date=None):

    if snapshot_date is None:
        snapshot_date = date.today().isoformat()

    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT COUNT(*)
            FROM asset_snapshots
            WHERE snapshot_date = ?
            """,
            (snapshot_date,),
        ).fetchone()

        return row[0] > 0

    finally:
        conn.close()


# =====================================================
# Portfolio Snapshot History
# =====================================================

def get_snapshots():
    """
    Return portfolio snapshots in chronological order.

    These are historical values persisted in the database.
    They must not be recalculated from today's market prices.
    """

    conn = get_connection()

    try:

        return conn.execute(
            """
            SELECT
                id,
                snapshot_date,
                invested,
                current_value,
                profit,
                return_pct,
                brokerage,
                dividend,
                bonus,
                created_at
            FROM portfolio_snapshots
            ORDER BY snapshot_date
            """
        ).fetchall()

    finally:
        conn.close()


# =====================================================
# Asset Snapshot History
# =====================================================

def get_asset_snapshots(asset_id=None):
    """
    Return historical asset snapshots.

    If asset_id is supplied, only that asset's history is returned.
    Otherwise all asset snapshots are returned.
    """

    conn = get_connection()

    try:

        if asset_id is None:

            return conn.execute(
                """
                SELECT
                    id,
                    snapshot_date,
                    asset_id,
                    quantity,
                    average_price,
                    market_price,
                    invested,
                    current,
                    profit,
                    allocation,
                    created_at
                FROM asset_snapshots
                ORDER BY
                    snapshot_date,
                    asset_id
                """
            ).fetchall()

        return conn.execute(
            """
            SELECT
                id,
                snapshot_date,
                asset_id,
                quantity,
                average_price,
                market_price,
                invested,
                current,
                profit,
                allocation,
                created_at
            FROM asset_snapshots
            WHERE asset_id = ?
            ORDER BY snapshot_date
            """,
            (asset_id,),
        ).fetchall()

    finally:
        conn.close()


# =====================================================
# Save Daily Snapshot
# =====================================================

def save_snapshot(snapshot_date=None):
    """
    Persist one portfolio snapshot for the supplied date.

    Existing snapshots are intentionally never overwritten.
    Historical snapshots must remain historical.
    """

    today = (
        snapshot_date
        if snapshot_date is not None
        else date.today().isoformat()
    )

    portfolio = get_portfolio()

    summary = portfolio["summary"]
    holdings = portfolio["holdings"]

    conn = get_connection()

    try:

        # -------------------------------------------------
        # Portfolio Snapshot
        # -------------------------------------------------

        if not snapshot_exists(today):

            conn.execute(
                """
                INSERT INTO portfolio_snapshots
                (
                    snapshot_date,
                    invested,
                    current_value,
                    profit,
                    return_pct,
                    brokerage,
                    dividend,
                    bonus
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    today,
                    summary["invested"],
                    summary["current"],
                    summary["total_pl"],
                    summary["return_pct"],
                    summary["brokerage"],
                    summary["dividend"],
                    summary["bonus"],
                ),
            )

        # -------------------------------------------------
        # Asset Snapshots
        # -------------------------------------------------

        if not asset_snapshot_exists(today):

            for holding in holdings:

                conn.execute(
                    """
                    INSERT INTO asset_snapshots
                    (
                        snapshot_date,
                        asset_id,
                        quantity,
                        average_price,
                        market_price,
                        invested,
                        current,
                        profit,
                        allocation
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        today,
                        holding["asset_id"],
                        holding["qty"],
                        holding["avg"],
                        holding["current_price"],
                        holding["invested"],
                        holding["current"],
                        holding["unrealized_pl"],
                        holding["allocation"],
                    ),
                )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()