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

    row = conn.execute(
        """
        SELECT id
        FROM portfolio_snapshots
        WHERE snapshot_date = ?
        """,
        (snapshot_date,),
    ).fetchone()

    conn.close()

    return row is not None


def asset_snapshot_exists(snapshot_date=None):

    if snapshot_date is None:
        snapshot_date = date.today().isoformat()

    conn = get_connection()

    row = conn.execute(
        """
        SELECT COUNT(*)
        FROM asset_snapshots
        WHERE snapshot_date = ?
        """,
        (snapshot_date,),
    ).fetchone()

    conn.close()

    return row[0] > 0


# =====================================================
# Snapshot History
# =====================================================

def get_snapshots():

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM portfolio_snapshots
        ORDER BY snapshot_date
        """
    ).fetchall()

    conn.close()

    return rows


# =====================================================
# Save Daily Snapshot
# =====================================================

def save_snapshot():

    print("\n==============================================")
    print("SAVE SNAPSHOT START")
    print("==============================================")

    today = date.today().isoformat()

    portfolio = get_portfolio()

    summary = portfolio["summary"]
    holdings = portfolio["holdings"]

    print("Holdings Found :", len(holdings))

    conn = get_connection()

    try:

        # -------------------------------------------------
        # Portfolio Snapshot
        # -------------------------------------------------

        if not snapshot_exists(today):

            print("Creating Portfolio Snapshot")

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
                    summary["profit"],
                    summary["return_pct"],
                    summary["brokerage"],
                    summary["dividend"],
                    summary["bonus"],
                ),
            )

        else:

            print("Portfolio Snapshot Already Exists")

        # -------------------------------------------------
        # Asset Snapshots
        # -------------------------------------------------

        if not asset_snapshot_exists(today):

            print("Creating Asset Snapshots")

            for holding in holdings:

                print(
                    "Saving:",
                    holding["symbol"],
                    "Asset ID:",
                    holding["asset_id"],
                )

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

        else:

            print("Asset Snapshots Already Exist")

        conn.commit()

        print("Commit Successful")

    except Exception as e:

        conn.rollback()

        print("\nERROR")
        print(type(e).__name__)
        print(e)

        raise

    finally:

        conn.close()

        print("Connection Closed")
        print("==============================================\n")