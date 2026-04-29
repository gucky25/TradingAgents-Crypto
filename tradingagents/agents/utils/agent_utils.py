from langchain_core.messages import HumanMessage, RemoveMessage

# Import tools from separate utility files
from tradingagents.agents.utils.core_stock_tools import (
    get_stock_data
)
from tradingagents.agents.utils.technical_indicators_tools import (
    get_indicators
)
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_insider_transactions,
    get_global_news
)


def get_language_instruction() -> str:
    """Return a prompt instruction for the configured output language.

    Returns empty string when English (default), so no extra tokens are used.
    Only applied to user-facing agents (analysts, portfolio manager).
    Internal debate agents stay in English for reasoning quality.
    """
    from tradingagents.dataflows.config import get_config
    lang = get_config().get("output_language", "English")
    if lang.strip().lower() == "english":
        return ""
    return f" Write your entire response in {lang}."


def get_instrument_type() -> str:
    """Return the configured instrument type, defaulting to crypto for this fork."""
    from tradingagents.dataflows.config import get_config

    instrument_type = get_config().get("instrument_type", "crypto")
    return str(instrument_type).strip().lower()


def is_crypto_instrument() -> bool:
    return get_instrument_type() == "crypto"


def build_instrument_context(ticker: str) -> str:
    """Describe the exact instrument so agents preserve the user's symbol."""
    exact_symbol = (
        f"The instrument to analyze is `{ticker}`. "
        "Use this exact symbol in every tool call, report, and recommendation, "
        "preserving any exchange suffix or crypto pair separator (e.g. `BTC-USD`, `ETH-USD`, `.TO`, `.L`, `.HK`, `.T`)."
    )

    if is_crypto_instrument():
        from tradingagents.dataflows.config import get_config

        config = get_config()
        quote_currency = config.get("quote_currency", "USD")
        benchmark = config.get("crypto_benchmark", "BTC-USD")
        return (
            exact_symbol
            + " Treat it as a 24/7 crypto asset or crypto pair, not as a company stock. "
            + f"Assume the quote currency is {quote_currency} unless the symbol states otherwise. "
            + f"Use {benchmark} as the default relative benchmark when judging outcomes or market beta. "
            + "Focus on price action, liquidity, volatility, volume, market structure, tokenomics, protocol/network health, regulatory catalysts, custody/security risk, and crypto-native sentiment. "
            + "Do not invent company filings, earnings, insider transactions, or balance-sheet metrics when they are not applicable."
        )

    return (
        exact_symbol
        + " Treat it as an equity or exchange-listed security with normal company fundamentals when applicable."
    )


def get_instrument_prompt_instruction() -> str:
    """Return extra prompt guidance for the configured instrument type."""
    if is_crypto_instrument():
        return (
            " Crypto mode is enabled: analyze the asset as a 24/7 crypto market, "
            "not as a company stock. Prefer crypto-native evidence such as liquidity, "
            "volume, volatility, funding/leverage context, tokenomics, network/protocol "
            "health, regulatory catalysts, custody/security risk, and crypto sentiment. "
            "When company financial statements or insider transactions are unavailable, "
            "state that they are not applicable instead of fabricating them."
        )
    return " Equity mode is enabled: analyze the instrument with stock-market and company-fundamental context where applicable."

def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]

        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]

        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")

        return {"messages": removal_operations + [placeholder]}

    return delete_messages


        
