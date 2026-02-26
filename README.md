# CSE-TRADE: Colombo Stock Exchange Desktop Analytics

**CSE-TRADE** is a premium, high-performance desktop application for monitoring and analyzing stocks on the Colombo Stock Exchange (CSE). Built with Python and PySide6, it provides a stable, offline-first experience with real-time data synchronization and interactive charting.

![CSE-TRADE Dashboard Preview1](https://raw.githubusercontent.com/charithmadhuranga/CSE-TRADE/refs/heads/master/dashboard1.png)
![CSE-TRADE Dashboard Preview](https://raw.githubusercontent.com/charithmadhuranga/CSE-TRADE/refs/heads/master/dashboard.png)

## 🚀 Key Features

- **Dynamic Dashboard**: Real-time tracking of market indices (ASPI, S&P SL20) and Top Gainers/Losers.
- **Advanced Stock Screener**: Filter and search through the entire CSE market with detailed trade summaries.
- **Interactive Technical Charts**:
  - High-performance plotting with `pyqtgraph`.
  - Automated axis scaling and manual downsampling for large datasets.
  - Built-in technical indicators: **RSI (14)**, **SMA (20)**, and **Volatility**.
- **Offline-First Architecture**: 
  - Integrated **SQLite Cache** provides instant UI loading from previous sessions.
  - Background **QThread SyncWorker** keeps data fresh without blocking the UI or causing crashes.
- **Premium Dark Aesthetics**: A professional-grade dark mode interface designed for readability and focus.

## 🛠 Tech Stack

- **UI Framework**: [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python).
- **Plotting**: [pyqtgraph](http://www.pyqtgraph.org/) for lightning-fast interactive charts.
- **Data Handling**: [pandas](https://pandas.pydata.org/) & [numpy](https://numpy.org/) for high-speed technical analysis.
- **Persistence**: [SQLite](https://sqlite.org/) for local data caching.
- **Project Management**: [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management.

## 📦 Installation & Setup

Ensure you have **Python 3.10+** and `uv` installed.

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

## 🏗 Architecture Overview

The application is designed for maximum stability on all platforms (including macOS ARM64):

- **`src/cse_trade/ui/`**: Contains the decoupled UI components (MainWindow, Dashboard, Screener, Charts).
- **`src/cse_trade/api/`**: Robust `CSEClient` with session-pooling and timeout management.
- **`src/cse_trade/core/`**: 
  - `DataStore`: Manages the SQLite cache layer.
  - `AnalyticsEngine`: Handles technical indicator calculations and data preprocessing.
- **`src/cse_trade/threads/`**: Houses the `SyncWorker` and `Worker` patterns for safe multi-threaded API interactions.

## 🛡 Stability & Performance

This version includes dedicated fixes for common Python/Qt pitfalls:
- **Segmentation Fault Protection**: Sequential background fetching prevents resource bursts.
- **NetRC Isolation**: Silenced native `netrc` lookups to prevent macOS-specific crashes in `requests`.
- **Memory Efficiency**: Downsampling logic handles stocks with 10+ years of price history without lag.

## 📜 License

[MIT License](LICENSE)

---
*Created for the Colombo Stock Exchange community.*
