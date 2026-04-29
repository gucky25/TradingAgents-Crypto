# Crypto Usage Guide

TradingAgents Crypto is a multi-agent crypto market analysis tool. It produces research reports and trading signals; it does not place live exchange orders.

## Quick Start

Install the project:

```bash
pip install .
```

Set your LLM provider key, for example:

```bash
set OPENAI_API_KEY=your_key_here
```

Run the CLI:

```bash
tradingagents analyze
```

Recommended first run:

- Instrument type: `Crypto`
- Symbol: `BTC-USD` or `ETH-USD`
- Crypto benchmark: `BTC-USD`
- Analysts: Market, Social, News, Fundamentals
- Research depth: Shallow for a quick check, Medium or Deep for richer debate

## Python Usage

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["instrument_type"] = "crypto"
config["crypto_benchmark"] = "BTC-USD"
config["data_vendors"] = {
    "core_stock_apis": "crypto,yfinance",
    "technical_indicators": "crypto,yfinance",
    "fundamental_data": "crypto,yfinance",
    "news_data": "yfinance",
}

ta = TradingAgentsGraph(
    selected_analysts=["market", "social", "news", "fundamentals"],
    config=config,
    debug=True,
)

state, decision = ta.propagate("ETH-USD", "2026-04-29")
print(decision)
```

## Supported Symbols

The first crypto provider uses Yahoo Finance-style crypto pairs:

- `BTC-USD`
- `ETH-USD`
- `SOL-USD`
- `BNB-USD`
- `XRP-USD`

Other pairs may work when the upstream provider supports them.

## What Changed For Crypto

- Prompts now treat instruments as crypto assets by default.
- Market analysis keeps the existing technical indicators but frames them for 24/7 crypto markets.
- Fundamentals no longer assumes company filings. It asks for tokenomics, protocol/network health, liquidity, market structure, custody/security risk, regulation, and adoption.
- Balance sheet, cash flow, income statement, and insider transaction tools return crypto-specific non-applicability guidance instead of fabricating company data.
- Memory-log outcome reflection compares against `crypto_benchmark` instead of hardcoded `SPY` when `instrument_type` is `crypto`.

## Limitations

This is a research and signal-generation tool, not an execution system.

It does not include:

- exchange API connections
- order placement
- wallet or custody management
- live portfolio reconciliation
- leverage/futures execution
- guaranteed stop-loss execution

Treat output as decision support. Use separate, tested risk and execution infrastructure before considering live trading.

## Equity Mode

Equity-style analysis is still available:

```python
config = DEFAULT_CONFIG.copy()
config["instrument_type"] = "equity"
config["equity_benchmark"] = "SPY"
```

The CLI also offers an `Equity / stock` instrument type.
