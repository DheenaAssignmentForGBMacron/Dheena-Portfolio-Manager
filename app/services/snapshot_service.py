"""
Snapshot Service

Persists historical portfolio and asset snapshots.

Snapshots are point-in-time records. Once a snapshot exists for a
date, it is never overwritten.
"""

from datetime import date

from app.database import database_connection
from app.services.portfolio_service import get_portfolio


def _normalize_date(snapshot_date=None):
    """Return the requested snapshot date."""

    return (
        snapshot_date
        if snapshot_date is not None
        else date.today().isoformat()
    )


# =====================================================
# Existence
# =====================================================

def snapshot_exists(snapshot_date=None):
    """Return whether a portfolio snapshot exists."""

    snapshot_date = _normalize_date(snapshot_date)

    with database_connection() as conn:

        row = conn.execute(
            """
            SELECT 1
            FROM portfolio_snapshots
            WHERE snapshot_date = ?
            LIMIT 1
            """,
            (snapshot_date,),
        ).fetchone()

        return row is not None


def asset_snapshot_exists(snapshot_date=None):
    """Return whether asset snapshots exist for a date."""

    snapshot_date = _normalize_date(snapshot_date)

    with database_connection() as conn:

        row = conn.execute(
            """
            SELECT 1
            FROM asset_snapshots
            WHERE snapshot_date = ?
            LIMIT 1
            """,
            (snapshot_date,),
        ).fetchone()

        return row is not None


# =====================================================
# Portfolio History
# =====================================================

def get_snapshots():
    """
    Return portfolio snapshots chronologically.

    `current_value` and `profit` are intentionally retained as
    compatibility aliases for existing analytics/frontend code.
    """

    with database_connection() as conn:

        return conn.execute(
            """
            SELECT
                id,
                snapshot_date,
                invested,

                current AS current_value,

                realized_pl,
                unrealized_pl,
                total_pl AS profit,

                return_pct,
                brokerage,
                dividend,
                bonus,
                created_at

            FROM portfolio_snapshots

            ORDER BY snapshot_date
            """
        ).fetchall()


# =====================================================
# Asset History
# =====================================================

def get_asset_snapshots(asset_id=None):
    """
    Return historical asset snapshots.

    When asset_id is supplied, only that asset's history is returned.
    """

    with database_connection() as conn:

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

                    realized_pl,
                    unrealized_pl,
                    total_pl AS profit,

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

                realized_pl,
                unrealized_pl,
                total_pl AS profit,

                allocation,
                created_at

            FROM asset_snapshots

            WHERE asset_id = ?

            ORDER BY snapshot_date
            """,
            (asset_id,),
        ).fetchall()


# =====================================================
# Save Snapshot
# =====================================================

def save_snapshot(snapshot_date=None):
    """
    Persist a portfolio snapshot and its asset snapshots.

    Snapshot creation is atomic:
    either the portfolio and all asset snapshots are persisted,
    or none of them are.
    """

    snapshot_date = _normalize_date(snapshot_date)

    portfolio = get_portfolio()

    summary = portfolio["summary"]
    holdings = portfolio["holdings"]

    with database_connection() as conn:

        # -------------------------------------------------
        # Portfolio Snapshot
        # -------------------------------------------------

        portfolio_exists = conn.execute(
            """
            SELECT 1
            FROM portfolio_snapshots
            WHERE snapshot_date = ?
            LIMIT 1
            """,
            (snapshot_date,),
        ).fetchone()

        if portfolio_exists is None:

            conn.execute(
                """
                INSERT INTO portfolio_snapshots
                (
                    snapshot_date,
                    invested,
                    current,
                    realized_pl,
                    unrealized_pl,
                    total_pl,
                    return_pct,
                    brokerage,
                    dividend,
                    bonus
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_date,
                    summary["invested"],
                    summary["current"],
                    summary["realized_pl"],
                    summary["unrealized_pl"],
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

        asset_exists = conn.execute(
            """
            SELECT 1
            FROM asset_snapshots
            WHERE snapshot_date = ?
            LIMIT 1
            """,
            (snapshot_date,),
        ).fetchone()

        if asset_exists is None:

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
                        realized_pl,
                        unrealized_pl,
                        total_pl,
                        allocation
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot_date,
                        holding["asset_id"],
                        holding["qty"],
                        holding["avg"],
                        holding["current_price"],
                        holding["invested"],
                        holding["current"],
                        holding["realized_pl"],
                        holding["unrealized_pl"],
                        holding["total_pl"],
                        holding["allocation"],
                    ),
                )