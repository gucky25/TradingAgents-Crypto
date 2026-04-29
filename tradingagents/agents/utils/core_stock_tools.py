from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_stock_data(
    symbol: Annotated[str, "ticker or crypto pair symbol, e.g. BTC-USD, ETH-USD, AAPL"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve price data (OHLCV) for a given instrument symbol.
    Uses the configured core_stock_apis vendor.
    Args:
        symbol (str): Instrument symbol, e.g. BTC-USD, ETH-USD, AAPL, TSM
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing OHLCV data for the specified symbol in the specified date range.
    """
    return route_to_vendor("get_stock_data", symbol, start_date, end_date)
