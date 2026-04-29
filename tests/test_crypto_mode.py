from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from tradingagents.agents.utils.agent_utils import build_instrument_context
from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.crypto import (
    get_crypto_balance_sheet,
    get_crypto_cashflow,
    get_crypto_income_statement,
)
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph


def _price_df(prices):
    return pd.DataFrame({"Close": prices})


@pytest.mark.unit
class TestCryptoMode:
    def test_instrument_context_is_crypto_specific(self):
        config = DEFAULT_CONFIG.copy()
        config["instrument_type"] = "crypto"
        config["crypto_benchmark"] = "BTC-USD"
        set_config(config)

        context = build_instrument_context("ETH-USD")

        assert "ETH-USD" in context
        assert "24/7 crypto asset" in context
        assert "BTC-USD" in context
        assert "Do not invent company filings" in context

    def test_crypto_statement_tools_return_non_applicable_guidance(self):
        for tool in (get_crypto_balance_sheet, get_crypto_cashflow, get_crypto_income_statement):
            result = tool("BTC-USD")
            assert "not applicable" in result
            assert "crypto asset 'BTC-USD'" in result

    def test_fetch_returns_uses_crypto_benchmark_from_config(self):
        asset_prices = [100.0, 110.0, 120.0, 130.0]
        benchmark_prices = [200.0, 202.0, 204.0, 206.0]
        mock_graph = MagicMock(spec=TradingAgentsGraph)
        mock_graph.config = {
            "instrument_type": "crypto",
            "crypto_benchmark": "BTC-USD",
        }

        seen_symbols = []

        with patch("yfinance.Ticker") as mock_ticker_cls:
            def _make_ticker(sym):
                seen_symbols.append(sym)
                m = MagicMock()
                m.history.return_value = _price_df(
                    benchmark_prices if sym == "BTC-USD" else asset_prices
                )
                return m

            mock_ticker_cls.side_effect = _make_ticker
            raw, relative, days = TradingAgentsGraph._fetch_returns(
                mock_graph, "ETH-USD", "2026-01-05", holding_days=3
            )

        assert seen_symbols == ["ETH-USD", "BTC-USD"]
        assert days == 3
        assert raw == pytest.approx(0.30)
        assert relative == pytest.approx(0.30 - 0.03)
