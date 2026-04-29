"""Crypto-oriented data helpers.

The first crypto implementation deliberately keeps dependencies small by
building on yfinance for aggregated OHLCV/news-compatible symbols such as
BTC-USD and ETH-USD. The module gives the rest of the system crypto-specific
headers and fundamentals text while preserving the existing vendor-router
shape, so a direct exchange provider can replace it later.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

import yfinance as yf

from .stockstats_utils import yf_retry
from .y_finance import get_stock_stats_indicators_window


def get_crypto_data(
    symbol: Annotated[str, "crypto pair symbol such as BTC-USD"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """Retrieve daily crypto OHLCV data for a Yahoo Finance-style pair."""
    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    ticker = yf.Ticker(symbol.upper())
    data = yf_retry(lambda: ticker.history(start=start_date, end=end_date))

    if data.empty:
        return f"No crypto market data found for '{symbol}' between {start_date} and {end_date}"

    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(4)

    header = f"# Crypto OHLCV data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Market type: 24/7 aggregated crypto market data\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    return header + data.to_csv()


def get_crypto_indicators(
    symbol: Annotated[str, "crypto pair symbol such as BTC-USD"],
    indicator: Annotated[str, "technical indicator to calculate"],
    curr_date: Annotated[str, "The current analysis date, YYYY-mm-dd"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    """Calculate technical indicators over crypto OHLCV data."""
    result = get_stock_stats_indicators_window(symbol, indicator, curr_date, look_back_days)
    return result.replace("##", f"## Crypto {symbol.upper()}", 1)


def get_crypto_fundamentals(
    ticker: Annotated[str, "crypto pair symbol such as BTC-USD"],
    curr_date: Annotated[str, "current date in YYYY-MM-DD format"] = None,
) -> str:
    """Return a crypto-focused fundamentals snapshot.

    yfinance exposes only a subset of crypto metadata. Missing fields are
    called out explicitly so the LLM does not confuse absent company filings
    with weak fundamentals.
    """
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        info = yf_retry(lambda: ticker_obj.info) or {}

        fields = [
            ("Name", info.get("longName") or info.get("shortName")),
            ("Symbol", info.get("symbol") or ticker.upper()),
            ("Quote Currency", info.get("currency")),
            ("Market Cap", info.get("marketCap")),
            ("Circulating Supply", info.get("circulatingSupply")),
            ("Total Supply", info.get("totalSupply")),
            ("Max Supply", info.get("maxSupply")),
            ("24h Volume", info.get("volume24Hr") or info.get("volume")),
            ("52 Week High", info.get("fiftyTwoWeekHigh")),
            ("52 Week Low", info.get("fiftyTwoWeekLow")),
            ("50 Day Average", info.get("fiftyDayAverage")),
            ("200 Day Average", info.get("twoHundredDayAverage")),
        ]

        lines = [
            f"# Crypto Fundamentals Snapshot for {ticker.upper()}",
            f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "This is not company financial-statement data. Evaluate crypto fundamentals through tokenomics, network adoption, liquidity, market structure, protocol/security risk, and regulatory context.",
            "",
        ]
        for label, value in fields:
            if value is not None:
                lines.append(f"{label}: {value}")

        if len(lines) <= 5:
            lines.append("No provider fundamentals were available for this crypto asset.")

        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving crypto fundamentals for {ticker}: {str(e)}"


def get_crypto_balance_sheet(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    return (
        f"Balance sheet data is not applicable to crypto asset '{ticker}'. "
        "Use tokenomics, treasury disclosures where available, protocol revenue, reserves, liquidity, and risk metrics instead."
    )


def get_crypto_cashflow(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    return (
        f"Cash flow statement data is not applicable to crypto asset '{ticker}'. "
        "For protocols, review fees, protocol revenue, incentives, emissions, and treasury runway where available."
    )


def get_crypto_income_statement(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    return (
        f"Income statement data is not applicable to crypto asset '{ticker}'. "
        "For protocol-style assets, consider fees, revenue share, token emissions, and demand for blockspace or services."
    )


def get_crypto_insider_transactions(ticker: str) -> str:
    return (
        f"Traditional insider transaction data is not applicable to crypto asset '{ticker}'. "
        "Use token unlock schedules, foundation/team wallet movements, exchange inflows/outflows, and governance disclosures instead."
    )
