import os
import requests
from typing import Optional, Dict
from datetime import datetime

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "demo")
INTERVAL = os.getenv("ALPHA_INTERVAL", "5min")

ALPHA_ENDPOINT = "https://www.alphavantage.co/query"

def fetch_latest_intraday(symbol: str, interval: str = None) -> Optional[Dict]:
    """
    Fetches latest intraday candle for symbol.
    Returns dict with keys: symbol, ts (YYYY-MM-DD HH:MM:SS), open, high, low, close, volume
    Returns None if data missing or API error.
    """
    if interval is None:
        interval = INTERVAL or "5min"

    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY,
        "outputsize": "compact",
        "datatype": "json"
    }

    try:
        resp = requests.get(ALPHA_ENDPOINT, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        raise RuntimeError(f"Failed to request data for {symbol}: {e}")

    # check for errors / rate-limit notes
    if "Note" in data:
        raise RuntimeError(f"AlphaVantage rate limit or note: {data.get('Note')}")
    if "Error Message" in data:
        raise RuntimeError(f"AlphaVantage error: {data.get('Error Message')}")

    # find time-series key
    time_series_key = next((k for k in data.keys() if k.startswith("Time Series")), None)
    if not time_series_key:
        return None

    time_series = data.get(time_series_key, {})
    if not time_series:
        return None

    # get latest timestamp (sorted keys)
    latest_ts_str = sorted(time_series.keys())[-1]
    latest = time_series[latest_ts_str]

    try:
        ts = datetime.fromisoformat(latest_ts_str)
    except Exception:
        # fallback: accept string as-is
        ts = latest_ts_str

    try:
        open_ = float(latest["1. open"])
        high = float(latest["2. high"])
        low = float(latest["3. low"])
        close = float(latest["4. close"])
        volume = int(latest["5. volume"])
    except Exception:
        return None

    return {
        "symbol": symbol,
        "ts": ts.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts, "strftime") else str(ts),
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume
    }
