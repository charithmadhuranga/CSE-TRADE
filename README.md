# CSE-TRADE: Colombo Stock Exchange Desktop Analytics

**CSE-TRADE** is a premium, high-performance desktop application for monitoring and analyzing stocks on the Colombo Stock Exchange (CSE). Built with Python and PySide6, it provides a stable, offline-first experience with real-time data synchronization, interactive charting, and AI-powered analysis.

![CSE-TRADE Dashboard Preview](https://raw.githubusercontent.com/charithmadhuranga/CSE-TRADE/refs/heads/master/dashboard.png)

## 🚀 Key Features

### Market Monitoring
- **Dynamic Dashboard**: Real-time tracking of market indices (ASPI, S&P SL20) and Top Gainers/Losers
- **Market Statistics**: Trade count, volume, turnover, advances/declines (calculated dynamically)
- **Auto-Refresh**: Configurable refresh interval (5-300 seconds)

### Stock Analysis
- **Advanced Stock Screener**: Filter and search through the entire CSE market
- **Interactive Technical Charts**: High-performance plotting with `pyqtgraph`
- **Stock Comparison**: Compare multiple stocks side-by-side
- **Remove/Compare**: Add/remove stocks from comparison with one click

### Portfolio Management
- **Holdings Tracker**: Track your portfolio with quantity, average price, and real-time P&L
- **Watchlist**: Monitor stocks with target price alerts
- **Transaction History**: Record and track all buy/sell transactions
- **Add/Remove Holdings**: Easily manage your portfolio positions

### AI-Powered Analysis
- **Agentic Chatbot**: Ask questions about CSE stocks and market trends using LangGraph
- **Multi-LLM Support**: Choose from OpenAI, Anthropic (Claude), Google Gemini, or Ollama
- **Offline Mode**: Basic data responses even without API configuration
- **Configurable Settings**: Set API keys and provider preferences

### Advanced Technical Indicators
- **Trend**: SMA, EMA, MACD, Bollinger Bands
- **Momentum**: RSI, Stochastic, Momentum, ROC
- **Volatility**: ATR, Bollinger Bands, Annualized Volatility
- **Volume**: OBV (On-Balance Volume)
- **Advanced**: CCI, Williams %R

### Advanced Statistics (Scipy & Scikit-learn)
- **Market Breadth**: Advances, declines, unchanged (calculated from trade data)
- **Performance Metrics**: Mean/median change, market sentiment (Bullish/Bearish/Neutral)
- **Volatility Metrics**: VaR 95%, CVaR, price range
- **Momentum Indicators**: Momentum score, t-statistic, p-value, significance
- **Percentile Ranks**: Price and volume percentiles
- **Clustering**: K-Means clustering of stocks
- **Distribution Analysis**: Skewness, kurtosis, market cap distribution

## 🛠 Tech Stack

- **UI Framework**: [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python)
- **Plotting**: [pyqtgraph](http://www.pyqtgraph.org/) for interactive charts
- **AI/LLM**: [LangGraph](https://langchain-ai.github.io/langgraph/) & [LangChain](https://langchain.com/)
- **Data Analysis**: [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/), [scipy](https://scipy.org/), [scikit-learn](https://scikit-learn.org/)
- **Persistence**: [SQLite](https://sqlite.org/) for local caching
- **Project Management**: [uv](https://github.com/astral-sh/uv)

## 📦 Installation & Setup

Ensure you have **Python 3.13+** and `uv` installed.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/charithmadhuranga/CSE-TRADE.git
   cd CSE-TRADE
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Run the application**:
   ```bash
   uv run run_app.py
   ```

## 🖥 Application Tabs

| Tab | Description |
|-----|-------------|
| **Dashboard** | Market indices, top gainers/losers |
| **Screener** | Filter & search CSE stocks |
| **Portfolio** | Holdings, P&L, transactions, watchlist |
| **Statistics** | Market overview, movers, advanced analytics |
| **Compare** | Side-by-side stock comparison |
| **AI Chat** | Agentic chatbot for market analysis |
| **Settings** | LLM provider, API keys, refresh interval |

## ⚙️ Settings

### Data Refresh
- **Refresh Interval**: Configure from 5 seconds to 5 minutes
- Auto-refresh keeps market data current without manual updates
- Data includes: Market Summary, Trade Summary, Top Gainers/Losers

### AI Chatbot Configuration

| Provider | API Key Required | Models |
|----------|------------------|--------|
| **OpenAI** | Yes | GPT-4o-mini, GPT-4o, GPT-4-turbo |
| **Anthropic** | Yes | Claude 3.5 Sonnet, Claude 3 Haiku |
| **Google Gemini** | Yes | Gemini 1.5 Pro, Gemini 1.5 Flash |
| **Ollama** | No | llama3.1, mistral (local) |

### Getting API Keys:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com
- **Google Gemini**: https://aistudio.google.com/app/apikey
- **Ollama**: https://ollama.com/download

## 📊 Statistics Engine Documentation

The application calculates advanced market statistics using scipy and scikit-learn. Below are the calculations and their assumptions:

### 1. Market Breadth (Advances/Declines/Unchanged)

| Metric | Calculation | Data Source |
|--------|-------------|--------------|
| **Advances** | Count of stocks with `change > 0` | `percentageChange` field from trade summary |
| **Declines** | Count of stocks with `change < 0` | `percentageChange` field from trade summary |
| **Unchanged** | Count of stocks with `change = 0` | `percentageChange` field from trade summary |

**Assumptions:**
- Uses `percentageChange` from CSE trade summary API
- If `percentageChange` is missing, stock is counted as unchanged
- Calculations are based on daily percentage change, not absolute price change

---

### 2. Market Sentiment

| Metric | Calculation | Data Source |
|--------|-------------|--------------|
| **Bullish** | Mean change > 0 | Average of all `percentageChange` values |
| **Bearish** | Mean change < 0 | Average of all `percentageChange` values |
| **Neutral** | Mean change = 0 | Average of all `percentageChange` values |

**Assumptions:**
- Uses simple mean of percentage changes (not weighted by market cap or volume)
- Sentiment is calculated fresh each time data is refreshed
- Threshold for bullish/bearish is strictly > 0 or < 0

---

### 3. Volatility Metrics

| Metric | Calculation | Formula |
|--------|-------------|---------|
| **Daily Volatility** | Standard deviation of daily changes | `σ = std(percentageChanges)` |
| **Annualized Volatility** | Daily vol × √252 | `σ_annual = σ × √252` |
| **VaR 95%** | 5th percentile of changes | `percentile(changes, 5)` |
| **CVaR 95%** | Mean of worst 5% of changes | `mean(changes[changes ≤ VaR])` |
| **Price Range** | Max change - Min change | `max - min` |

**Assumptions:**
- Changes are in percentage form (e.g., 1.5 = 1.5%)
- Annualized using 252 trading days (standard for stocks)
- VaR assumes normal distribution of returns (parametric)
- CVaR is the expected loss given the loss exceeds VaR

---

### 4. Momentum Indicators

| Metric | Calculation | Formula |
|--------|-------------|---------|
| **Momentum Score** | Weighted average of changes | `Σ(sign(change) × |change|) / n` |
| **Positive Ratio** | % of stocks with positive change | `(positive_count / total) × 100` |
| **T-Statistic** | Mean / (std / √n) | `t = μ / (σ / √n)` |
| **P-Value** | Statistical significance | From t-distribution |
| **Significant** | P-value < 0.05 | Boolean |

**Assumptions:**
- Momentum direction: UP if score > 0.5, DOWN if < -0.5, else SIDEWAYS
- Statistical significance uses 95% confidence level (α = 0.05)
- T-test assumes approximately normal distribution of changes

---

### 5. Price Statistics

| Metric | Calculation |
|--------|-------------|
| **Mean Price** | Average of all stock prices |
| **Median Price** | Middle value of sorted prices |
| **Min/Max Price** | Lowest and highest prices |
| **Std Dev** | Standard deviation of prices |
| **Skewness** | Measure of asymmetry (scipy.stats.skew) |
| **Kurtosis** | Measure of tail heaviness (scipy.stats.kurtosis) |

**Assumptions:**
- Only stocks with price > 0 are included
- Skewness/Kurtosis use Fisher's definition (normal = 0)

---

### 6. Volume Statistics

| Metric | Calculation |
|--------|-------------|
| **Total Volume** | Sum of all `tradevolume` |
| **Average Volume** | Mean of all volumes |
| **Median Volume** | Middle value of volumes |
| **Volume Std** | Standard deviation of volumes |

**Assumptions:**
- Uses `tradevolume` field from CSE API (not `sharevolume`)
- Volume is in shares traded

---

### 7. Percentile Ranks

| Metric | Calculation |
|--------|-------------|
| **Price Percentile** | Rank of stock's price among all stocks |
| **Volume Percentile** | Rank of stock's volume among all stocks |
| **Composite Score** | Average of price and volume percentiles |

**Assumptions:**
- Uses scipy.stats.rankdata with 'average' method
- Percentiles range from 0-100%
- Higher percentile = higher rank

---

### 8. K-Means Clustering

| Metric | Calculation |
|--------|-------------|
| **Features** | Normalized price, volume, change |
| **Algorithm** | K-Means with k=5 clusters |
| **Scaling** | StandardScaler (z-score normalization) |

**Assumptions:**
- Uses 5 clusters by default
- Random state = 42 for reproducibility
- Stocks with zero price/volume are excluded

---

### Data Source

All statistics are calculated from the CSE Trade Summary API endpoint (`/tradeSummary`), which provides:
- `symbol`: Stock symbol
- `price`: Current trading price
- `percentageChange`: Daily percentage change
- `tradevolume`: Number of shares traded
- `marketCap`: Market capitalization
- Other fields like high, low, turnover

**Note:** Sector performance is NOT available from the CSE API, so it is not displayed.

---

## 🏗 Architecture Overview

```
src/cse_trade/
├── api/
│   └── client.py          # CSE API client
├── agents/
│   ├── chatbot.py         # LangGraph agent
│   └── providers.py       # LLM provider factory
├── core/
│   ├── cache.py          # SQLite cache layer
│   ├── models.py         # Technical indicators
│   ├── portfolio.py     # Portfolio management
│   └── statistics.py     # Advanced statistics engine
├── threads/
│   └── workers.py        # Background workers
└── ui/
    ├── main_window.py    # Main application window
    ├── dashboard.py      # Market dashboard
    ├── screener.py       # Stock screener
    ├── charts.py         # Technical charts
    ├── chat.py           # Chatbot UI
    ├── portfolio.py      # Portfolio widget
    ├── analytics.py      # Statistics & comparison
    └── settings.py       # Settings UI
```

## 🛡 Stability & Performance

- **Offline-First**: SQLite cache provides instant UI loading
- **Background Sync**: QThread workers keep data fresh without blocking UI
- **Auto-Refresh**: Configurable 5-300 second intervals
- **Memory Efficiency**: Downsampling handles 10+ years of price history
- **Segmentation Fault Protection**: Sequential background fetching
- **NetRC Isolation**: Prevents macOS-specific crashes

## 📜 License

[MIT License](LICENSE)

---

*Built for the Colombo Stock Exchange community.*
