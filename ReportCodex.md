# Codex rapport: crypto-geschiktheid van dit TradingAgents project

Datum: 2026-04-29

## Korte conclusie

Dit project is primair een multi-agent analyse- en beslissingsframework voor aandelen, geen kant-en-klare trading bot. Het kan beperkt worden gebruikt voor crypto-analyse, vooral voor OHLCV/technische analyse via Yahoo Finance-achtige symbolen zoals `BTC-USD`, maar het is out-of-the-box niet geschikt om veilig en automatisch cryptovaluta te verhandelen.

De architectuur is wel goed aanpasbaar. De belangrijkste reden is dat de datalaag al een vendor-router heeft (`tradingagents/dataflows/interface.py`) en de agents via abstracte tools werken (`tradingagents/agents/utils/*_tools.py`). Daardoor kan een crypto-dataprovider relatief schoon worden toegevoegd. Voor echte crypto-trading ontbreken echter nog exchange-connectors, orderuitvoering, portefeuillebeheer, 24/7-marktlogica, crypto-specifieke risico's en crypto-specifieke prompts/data.

## Wat het project nu doet

Het centrale proces staat in `tradingagents/graph/trading_graph.py` en loopt grofweg als volgt:

1. Analyst agents verzamelen marktdata, nieuws, sentiment en fundamentals.
2. Bull/Bear researchers debatteren over de investment case.
3. De Research Manager maakt een investment plan.
4. De Trader zet dit om naar Buy/Hold/Sell met entry, stop-loss en sizing.
5. Risk analysts debatteren over het voorstel.
6. De Portfolio Manager geeft de finale rating: Buy, Overweight, Hold, Underweight of Sell.

Belangrijk: deze output is een advies/signaal in tekstvorm. Ik heb geen code gevonden die live orders plaatst bij Binance, Coinbase, Kraken, Bybit, OKX, Alpaca of een andere broker/exchange. De README noemt een "simulated exchange", maar in de huidige code zie ik vooral rapportage, signal extraction en memory logging; geen uitgewerkte order-engine of exchange-adapter.

## Componentanalyse voor crypto

### 1. Datalaag

Relevante bestanden:

- `tradingagents/dataflows/interface.py`
- `tradingagents/dataflows/y_finance.py`
- `tradingagents/dataflows/alpha_vantage_stock.py`
- `tradingagents/dataflows/alpha_vantage_news.py`
- `tradingagents/default_config.py`

De datalaag routeert tools naar `yfinance` of `alpha_vantage`. Dat is positief voor uitbreidbaarheid. De huidige categorieen heten echter `core_stock_apis`, `technical_indicators`, `fundamental_data` en `news_data`, en veel functienamen/documentatie spreken expliciet over aandelen, tickers en bedrijven.

Voor crypto is dit deels bruikbaar:

- Yahoo Finance kan in de praktijk vaak crypto-pairs zoals `BTC-USD` of `ETH-USD` leveren, waardoor `get_stock_data` en de technische indicatoren waarschijnlijk bruikbaar zijn voor basisanalyse.
- `stockstats` werkt op OHLCV-data en is niet principieel aandelen-only.
- Alpha Vantage news heeft in de docstring al dekking voor cryptocurrencies en forex, dus nieuws/sentiment is conceptueel bruikbaar.

Beperkingen:

- `alpha_vantage_stock.py` gebruikt `TIME_SERIES_DAILY_ADJUSTED`, een equity-georienteerde endpointkeuze.
- Er is geen crypto-exchange data zoals orderbook, trades, spreads, funding rates, open interest, liquidations, staking/on-chain metrics of exchange flows.
- De tool-API is daggericht en niet ontworpen voor intraday/24-7 crypto-markten.

### 2. Technische analyse

Relevante bestanden:

- `tradingagents/agents/analysts/market_analyst.py`
- `tradingagents/agents/utils/technical_indicators_tools.py`
- `tradingagents/dataflows/stockstats_utils.py`

Dit is het meest herbruikbare deel. Indicatoren zoals SMA, EMA, MACD, RSI, Bollinger Bands, ATR, VWMA en MFI zijn ook voor crypto bruikbaar, mits de inputdata goed is.

Aanpassingen die ik zou doen:

- Hernoem generieke functies van `stock` naar `market` of `instrument`, bijvoorbeeld `get_stock_data` naar `get_price_data`.
- Voeg intervalkeuze toe, bijvoorbeeld `1h`, `4h`, `1d`, omdat crypto vaak intraday wordt geanalyseerd.
- Zorg dat weekends niet als "not a trading day" worden behandeld voor crypto.
- Gebruik UTC en expliciete exchange timestamps.

### 3. Fundamentals

Relevante bestanden:

- `tradingagents/agents/analysts/fundamentals_analyst.py`
- `tradingagents/agents/utils/fundamental_data_tools.py`
- `tradingagents/dataflows/y_finance.py`
- `tradingagents/dataflows/alpha_vantage_fundamentals.py`

Dit onderdeel is sterk aandelen-specifiek. De code vraagt om bedrijfsprofielen, balans, cashflow, income statement, ratios, insider transactions en company fundamentals. Voor Bitcoin, Ether en veel tokens bestaan die datatypes niet in dezelfde vorm.

Voor crypto moet dit worden vervangen door een crypto-fundamentals module, bijvoorbeeld:

- tokenomics: supply, unlocks, issuance, burn mechanics
- protocol metrics: fees, revenue, TVL, active addresses
- network health: hashrate, staking ratio, validator metrics
- liquidity: exchange volume, orderbook depth, spreads
- market structure: funding rates, open interest, liquidation clusters
- regulatory/security: hacks, bridge risk, issuer/custody risk

Voor een eerste MVP zou ik de Fundamentals Analyst uitschakelen bij crypto of vervangen door een Crypto Fundamentals Analyst.

### 4. Nieuws en sentiment

Relevante bestanden:

- `tradingagents/agents/analysts/news_analyst.py`
- `tradingagents/agents/analysts/social_media_analyst.py`
- `tradingagents/dataflows/yfinance_news.py`
- `tradingagents/dataflows/alpha_vantage_news.py`

Dit is deels bruikbaar, maar de prompts zijn nog "company specific". Crypto heeft vaak asset-, protocol-, exchange-, macro- en regulatory nieuws nodig. De globale Yahoo Finance zoekqueries zijn nu stock/economy georienteerd, bijvoorbeeld "stock market economy".

Aanbevolen aanpassingen:

- Maak nieuwsqueries asset-aware: `BTC`, `Bitcoin`, `spot ETF`, `mining`, `hashrate`, `regulation`, `stablecoins`, enzovoort.
- Voeg crypto-specifieke bronnen toe of gebruik een provider die crypto-nieuws en sentiment gestructureerd aanbiedt.
- Pas de Social Media Analyst aan naar crypto-community sentiment, waarbij hype/manipulatie expliciet als risico wordt benoemd.

### 5. Agent-prompts en terminologie

Relevante bestanden:

- `tradingagents/agents/researchers/bull_researcher.py`
- `tradingagents/agents/researchers/bear_researcher.py`
- `tradingagents/agents/risk_mgmt/*.py`
- `tradingagents/agents/managers/research_manager.py`
- `tradingagents/agents/trader/trader.py`
- `tradingagents/agents/managers/portfolio_manager.py`

Veel prompts spreken over "stock", "company", "financial documents", "competitive advantages", "market saturation" en "company fundamentals". Dat stuurt de LLM richting aandelenanalyse, ook als het symbool `BTC-USD` is.

Voor crypto moet de prompt-context een instrumenttype krijgen, bijvoorbeeld:

```text
instrument_type: crypto
base_asset: BTC
quote_asset: USD
venue: aggregated or exchange-specific
market_hours: 24/7
```

Daarna kunnen agents conditioneel andere instructies krijgen. Voor crypto moeten ze bijvoorbeeld rekening houden met liquiditeit, leverage, funding, custody, regulatory events, token unlocks en protocol/security risks.

### 6. Memory log en benchmark

Relevante bestanden:

- `tradingagents/graph/trading_graph.py`
- `tradingagents/graph/reflection.py`
- `tradingagents/agents/utils/memory.py`

De memory log vergelijkt gerealiseerde returns met `SPY`. Voor crypto is dat meestal geen passende benchmark. In `TradingAgentsGraph._fetch_returns` wordt naast het instrument altijd `SPY` opgehaald, en `Reflector` noemt expliciet "Alpha vs SPY".

Voor crypto zou dit configureerbaar moeten worden:

- BTC trading: benchmark eventueel `BTC-USD` of een crypto-index.
- Altcoins: benchmark vaak `BTC-USD`, `ETH-USD` of een marktcap-gewogen crypto benchmark.
- Stablecoin/market-neutral strategieen: benchmark mogelijk cash/stablecoin yield of 0%.

### 7. Trading/executie

In de huidige code zie ik geen echte orderuitvoering. De output is een advies/rating, geen orderticket dat naar een exchange wordt gestuurd.

Voor live of paper crypto trading zijn minimaal nodig:

- Exchange adapter, bijvoorbeeld via CCXT of directe exchange REST/WebSocket API.
- Paper trading mode voordat live trading mogelijk is.
- Ordermodellen: market, limit, stop, reduce-only, post-only, time-in-force.
- Portfolio state: balances, open positions, average entry, unrealized PnL.
- Risk engine: max position size, max daily loss, leverage cap, stop-loss enforcement.
- Kostenmodel: fees, spread, slippage, funding, borrow/leverage costs.
- Secrets management voor API keys met withdrawal-permissions uitgeschakeld.
- Audit log en kill switch.

Zonder deze laag is het project beter te classificeren als "decision support" dan als "trading system".

## Kan het nu al crypto analyseren?

Ja, beperkt:

- Kies alleen `market`, `news` en eventueel `social` analysts.
- Gebruik een Yahoo Finance-achtig crypto-symbool zoals `BTC-USD`.
- Vermijd of negeer de Fundamentals Analyst, omdat die stock/company data verwacht.
- Interpreteer de uitkomst als research-signaal, niet als uitvoerbare trade.

Voorbeeldrichting in Python:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "news_data": "alpha_vantage,yfinance",
    "fundamental_data": "yfinance",
}

ta = TradingAgentsGraph(
    selected_analysts=["market", "news", "social"],
    config=config,
    debug=True,
)

state, decision = ta.propagate("BTC-USD", "2026-04-29")
print(decision)
```

Let op: dit blijft analyse. Het plaatst geen order.

## Aanbevolen aanpassingspad

### MVP: crypto-analyse zonder live trading

1. Voeg een `instrument_type` toe aan state/config: `equity` of `crypto`.
2. Maak stock-termen generiek in toolnamen en prompts.
3. Sla de Fundamentals Analyst over voor crypto of vervang deze door `Crypto Fundamentals Analyst`.
4. Voeg crypto benchmarks toe en verwijder de vaste SPY-aanname.
5. Voeg tests toe voor `BTC-USD`, `ETH-USD` en weekenddatums.

### Versie 2: crypto-data professioneel maken

1. Voeg `tradingagents/dataflows/crypto_exchange.py` toe.
2. Breid `VENDOR_LIST` en `VENDOR_METHODS` uit met een crypto vendor.
3. Ondersteun OHLCV intervals, orderbook snapshots, trades, funding rates en open interest.
4. Voeg provider-specifieke foutafhandeling, rate limits en caching toe.
5. Maak de CLI duidelijk: asset class, base/quote, venue en interval.

### Versie 3: paper/live trading

1. Bouw eerst een paper exchange adapter.
2. Maak een `OrderIntent` uit de Portfolio Manager output in plaats van alleen markdown.
3. Voeg pre-trade risk checks toe.
4. Voeg order execution en reconciliation toe.
5. Zet live trading achter expliciete feature flags en restrictieve API-key permissies.

## Belangrijkste risico's bij crypto-aanpassing

- LLM-output is niet deterministisch genoeg om zonder harde risk checks orders te plaatsen.
- Crypto is 24/7; weekend/holiday-aannames kunnen tot verkeerde datagaten leiden.
- Fundamentals in de huidige vorm zijn ongeschikt voor non-company assets.
- SPY-alpha is voor crypto meestal misleidend.
- Live trading vereist veel meer infrastructuur dan een analysegraph: credentials, order state, retries, partial fills, slippage, fees en fail-safes.

## Eindadvies

Gebruik dit project voor crypto eerst als research- en signaleringslaag. De bestaande agentgraph, technische indicatoren, rapportage, structured output en memory log zijn waardevol. Pas daarna pas de datalaag en prompts aan voor crypto. Voor echte handel moet er een aparte, streng geteste execution- en risk-laag bij komen; die ontbreekt nu.

Mijn inschatting:

- Geschikt voor aandelenanalyse: ja, conform huidige opzet.
- Geschikt voor beperkte crypto-analyse: ja, met vooral market/news/social en Yahoo Finance-symbolen.
- Geschikt voor automatische crypto-trading: nee, niet zonder substantiële uitbreiding.
- Goed aanpasbaar richting crypto: ja, dankzij de modulaire vendor-router en agent-tool scheiding.
