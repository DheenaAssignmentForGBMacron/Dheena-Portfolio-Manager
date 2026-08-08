from app.repositories.asset_repository import AssetRepository

_repository = AssetRepository()


# =====================================================
# Create
# =====================================================

def add_asset(
    symbol,
    name,
    asset_class,
    exchange,
):
    return _repository.add(
        symbol,
        name,
        asset_class,
        exchange,
    )


# =====================================================
# Read
# =====================================================

def get_assets():
    return _repository.get_all()


def get_asset(asset_id):
    return _repository.get(asset_id)


def search_assets(search_text):
    return _repository.search(search_text)


# =====================================================
# Summary
# =====================================================

def get_asset_summary():
    return _repository.get_summary()


# =====================================================
# Seed
# =====================================================

def seed_assets():

    assets = [

        ("HAL", "Hindustan Aeronautics Ltd", "Stock", "NSE"),
        ("BSE", "BSE Ltd", "Stock", "NSE"),
        ("TATAMOTORS", "Tata Motors Ltd", "Stock", "NSE"),
        ("ANGELONE", "Angel One Ltd", "Stock", "NSE"),
        ("ADANIPORTS", "Adani Ports & SEZ Ltd", "Stock", "NSE"),
        ("ADANIENSOL", "Adani Energy Solutions Ltd", "Stock", "NSE"),
        ("BEML", "BEML Ltd", "Stock", "NSE"),
        ("AFCONS", "Afcons Infrastructure Ltd", "Stock", "NSE"),

        ("SILVERBEES", "Nippon India Silver ETF", "ETF", "NSE"),

        ("NIFTYBEES", "Nippon India ETF Nifty 50", "ETF", "NSE"),

    ]

    return _repository.seed(assets)