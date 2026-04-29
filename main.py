from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-5.4-mini"  # Use a different model
config["quick_think_llm"] = "gpt-5.4-mini"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds

# Crypto analysis configuration (default uses yfinance-style crypto pairs)
config["instrument_type"] = "crypto"
config["crypto_benchmark"] = "BTC-USD"

# Configure data vendors (crypto routes OHLCV/indicators/fundamentals through crypto-aware wrappers)
config["data_vendors"] = {
    "core_stock_apis": "crypto,yfinance",       # Options: crypto, alpha_vantage, yfinance
    "technical_indicators": "crypto,yfinance",  # Options: crypto, alpha_vantage, yfinance
    "fundamental_data": "crypto,yfinance",      # Options: crypto, alpha_vantage, yfinance
    "news_data": "yfinance",                    # Options: alpha_vantage, yfinance
}

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("BTC-USD", "2026-04-29")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
