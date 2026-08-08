"""
Price Service

Responsible for providing market prices.

Current implementation:
- Mock Prices

Future implementations:
- Yahoo Finance
- NSE
- AlphaVantage
- Manual Upload
"""


# =====================================================
# Mock Price Provider
# =====================================================

_MOCK_PRICES = {

    # -------------------------------------------------
    # Existing Test Assets
    # -------------------------------------------------

    "HAL": 400.00,
    "BSE": 1250.00,
    "BEML": 1000.00,
    "STALLION": 125.00,
    "DMY": 120.00,

    # -------------------------------------------------
    # FIFO / P&L Test Asset
    # -------------------------------------------------

    "TF1": 130.00,
}


# =====================================================
# Internal Provider
# =====================================================

def _mock_price(symbol):
    """
    Return the mock market price for a symbol.

    Returns None when:
    - symbol is missing
    - no mock price exists
    """

    if not symbol:
        return None

    return _MOCK_PRICES.get(symbol.upper())


# =====================================================
# Public API
# =====================================================

def get_price(symbol):
    """
    Return the latest market price.

    This is the ONLY function that the rest of DPM
    should call for market prices.

    The underlying provider can be replaced later
    without changing the rest of the application.
    """

    return _mock_price(symbol)


# =====================================================
# Batch Prices
# =====================================================

def get_prices(symbols):
    """
    Return market prices for multiple symbols.

    Future API implementations can request all prices
    in a single network call.
    """

    return {
        symbol: get_price(symbol)
        for symbol in symbols
    }


# =====================================================
# Provider Information
# =====================================================

def get_provider():
    """
    Return the name of the active price provider.
    """

    return "Mock Provider"