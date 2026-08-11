-- =====================================================
-- Assets
-- =====================================================

CREATE TABLE IF NOT EXISTS assets (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    symbol TEXT NOT NULL UNIQUE,

    name TEXT NOT NULL,

    asset_class TEXT NOT NULL,

    exchange TEXT,

    sector TEXT,

    isin TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP

);


-- =====================================================
-- Transactions
-- =====================================================

CREATE TABLE IF NOT EXISTS transactions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    asset_id INTEGER,

    asset TEXT NOT NULL,

    asset_type TEXT NOT NULL,

    transaction_type TEXT NOT NULL,

    quantity REAL NOT NULL,

    price REAL NOT NULL,

    brokerage REAL DEFAULT 0,

    dividend REAL DEFAULT 0,

    bonus REAL DEFAULT 0,

    transaction_date DATE NOT NULL,

    notes TEXT,

    FOREIGN KEY (asset_id)
        REFERENCES assets(id)

);

CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    snapshot_date DATE NOT NULL UNIQUE,

    invested REAL NOT NULL,
    current REAL NOT NULL,

    realized_pl REAL NOT NULL,
    unrealized_pl REAL NOT NULL,
    total_pl REAL NOT NULL,

    return_pct REAL NOT NULL,

    brokerage REAL NOT NULL,
    dividend REAL NOT NULL,
    bonus REAL NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asset_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    snapshot_date DATE NOT NULL,

    asset_id INTEGER NOT NULL,

    quantity REAL NOT NULL,
    average_price REAL NOT NULL,
    market_price REAL NOT NULL,

    invested REAL NOT NULL,
    current REAL NOT NULL,

    realized_pl REAL NOT NULL,
    unrealized_pl REAL NOT NULL,
    total_pl REAL NOT NULL,

    allocation REAL NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(snapshot_date, asset_id),

    FOREIGN KEY (asset_id)
        REFERENCES assets(id)
);

-- =====================================================
-- Performance Indexes
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_transactions_asset_id
    ON transactions(asset_id);

CREATE INDEX IF NOT EXISTS idx_transactions_asset_date
    ON transactions(asset_id, transaction_date, id);

CREATE INDEX IF NOT EXISTS idx_transactions_date
    ON transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_asset_snapshots_asset_date
    ON asset_snapshots(asset_id, snapshot_date);

CREATE INDEX IF NOT EXISTS idx_asset_snapshots_date
    ON asset_snapshots(snapshot_date);