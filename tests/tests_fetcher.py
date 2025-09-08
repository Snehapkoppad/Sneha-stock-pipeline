import os
import pytest
from lib.fetcher import fetch_latest_intraday

def test_fetch_latest_intraday(monkeypatch):
    # Make sure API key is set before running real test
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        pytest.skip("No ALPHAVANTAGE_API_KEY set")

    data = fetch_latest_intraday("AAPL")
    assert data is not None
    assert "symbol" in data
    assert data["symbol"] == "AAPL"
    assert "price" in data
    assert isinstance(data["price"], float)

