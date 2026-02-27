from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QGroupBox,
    QScrollArea,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class StatisticsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("Market Statistics")
        title.setStyleSheet("""
            QLabel {
                color: #00e676;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #121212;
            }
        """)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)

        self.market_stats_group = self._create_market_stats_group()
        content_layout.addWidget(self.market_stats_group)

        self.movers_group = self._create_movers_group()
        content_layout.addWidget(self.movers_group)

        self.sector_group = self._create_sector_group()
        content_layout.addWidget(self.sector_group)

        content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _create_market_stats_group(self) -> QGroupBox:
        group = QGroupBox("Market Overview")
        group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QGridLayout()
        layout.setSpacing(15)

        self.trade_count_label = self._create_stat_label("0")
        self.total_volume_label = self._create_stat_label("0")
        self.total_turnover_label = self._create_stat_label("Rs. 0")
        self.advances_label = self._create_stat_label("0")
        self.declines_label = self._create_stat_label("0")
        self.unchanged_label = self._create_stat_label("0")

        layout.addWidget(QLabel("Trade Count:"), 0, 0)
        layout.addWidget(self.trade_count_label, 0, 1)
        layout.addWidget(QLabel("Total Volume:"), 0, 2)
        layout.addWidget(self.total_volume_label, 0, 3)
        layout.addWidget(QLabel("Total Turnover:"), 1, 0)
        layout.addWidget(self.total_turnover_label, 1, 1)
        layout.addWidget(QLabel("Advances:"), 1, 2)
        layout.addWidget(self.advances_label, 1, 3)
        layout.addWidget(QLabel("Declines:"), 2, 0)
        layout.addWidget(self.declines_label, 2, 1)
        layout.addWidget(QLabel("Unchanged:"), 2, 2)
        layout.addWidget(self.unchanged_label, 2, 3)

        group.setLayout(layout)
        return group

    def _create_movers_group(self) -> QGroupBox:
        group = QGroupBox("Market Movers")
        group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(20)

        gainers_layout = QVBoxLayout()
        gainers_label = QLabel("Top Gainers")
        gainers_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        gainers_layout.addWidget(gainers_label)

        self.top_gainers_table = QTableWidget(5, 3)
        self.top_gainers_table.setHorizontalHeaderLabels(["Symbol", "Price", "Change"])
        self.top_gainers_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: none;
                gridline-color: #444;
            }
            QTableWidget::item { padding: 5px; }
            QHeaderView::section {
                background-color: #333;
                color: #e0e0e0;
                padding: 5px;
                border: none;
            }
        """)
        self.top_gainers_table.horizontalHeader().setStretchLastSection(True)
        self.top_gainers_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        gainers_layout.addWidget(self.top_gainers_table)

        losers_layout = QVBoxLayout()
        losers_label = QLabel("Top Losers")
        losers_label.setStyleSheet("color: #f44336; font-weight: bold;")
        losers_layout.addWidget(losers_label)

        self.top_losers_table = QTableWidget(5, 3)
        self.top_losers_table.setHorizontalHeaderLabels(["Symbol", "Price", "Change"])
        self.top_losers_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: none;
                gridline-color: #444;
            }
            QTableWidget::item { padding: 5px; }
            QHeaderView::section {
                background-color: #333;
                color: #e0e0e0;
                padding: 5px;
                border: none;
            }
        """)
        self.top_losers_table.horizontalHeader().setStretchLastSection(True)
        self.top_losers_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        losers_layout.addWidget(self.top_losers_table)

        layout.addLayout(gainers_layout, 1)
        layout.addLayout(losers_layout, 1)

        group.setLayout(layout)
        return group

    def _create_sector_group(self) -> QGroupBox:
        group = QGroupBox("Market Analytics")
        group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QGridLayout()
        layout.setSpacing(15)

        # Row 1: Market Sentiment & Momentum
        self.sentiment_label = QLabel("Sentiment: -")
        self.sentiment_label.setStyleSheet("color: #e0e0e0; font-size: 14px;")

        self.momentum_label = QLabel("Momentum: -")
        self.momentum_label.setStyleSheet("color: #e0e0e0; font-size: 14px;")

        # Row 2: Price Stats
        self.price_mean_label = QLabel("Avg Price: -")
        self.price_mean_label.setStyleSheet("color: #00e676;")

        self.price_median_label = QLabel("Median: -")
        self.price_median_label.setStyleSheet("color: #00e676;")

        # Row 3: Volatility
        self.volatility_label = QLabel("Volatility: -")
        self.volatility_label.setStyleSheet("color: #ff9800;")

        self.var_label = QLabel("VaR 95%: -")
        self.var_label.setStyleSheet("color: #ff9800;")

        # Row 4: Volume
        self.volume_total_label = QLabel("Total Volume: -")
        self.volume_total_label.setStyleSheet("color: #2196f3;")

        self.volume_avg_label = QLabel("Avg Volume: -")
        self.volume_avg_label.setStyleSheet("color: #2196f3;")

        # Row 5: Performance
        self.mean_change_label = QLabel("Mean Change: -")
        self.mean_change_label.setStyleSheet("color: #e0e0e0;")

        self.positive_ratio_label = QLabel("Positive: -")
        self.positive_ratio_label.setStyleSheet("color: #e0e0e0;")

        layout.addWidget(QLabel("Market Sentiment:"), 0, 0)
        layout.addWidget(self.sentiment_label, 0, 1)
        layout.addWidget(QLabel("Momentum:"), 0, 2)
        layout.addWidget(self.momentum_label, 0, 3)

        layout.addWidget(QLabel("Avg Price:"), 1, 0)
        layout.addWidget(self.price_mean_label, 1, 1)
        layout.addWidget(QLabel("Median Price:"), 1, 2)
        layout.addWidget(self.price_median_label, 1, 3)

        layout.addWidget(QLabel("Volatility:"), 2, 0)
        layout.addWidget(self.volatility_label, 2, 1)
        layout.addWidget(QLabel("VaR 95%:"), 2, 2)
        layout.addWidget(self.var_label, 2, 3)

        layout.addWidget(QLabel("Total Volume:"), 3, 0)
        layout.addWidget(self.volume_total_label, 3, 1)
        layout.addWidget(QLabel("Avg Volume:"), 3, 2)
        layout.addWidget(self.volume_avg_label, 3, 3)

        layout.addWidget(QLabel("Mean Change:"), 4, 0)
        layout.addWidget(self.mean_change_label, 4, 1)
        layout.addWidget(QLabel("Positive Ratio:"), 4, 2)
        layout.addWidget(self.positive_ratio_label, 4, 3)

        group.setLayout(layout)
        return group
        return group

    def _create_stat_label(self, value: str) -> QLabel:
        label = QLabel(value)
        label.setStyleSheet("""
            QLabel {
                color: #00e676;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        return label

    def update_market_stats(self, data: dict):
        if not data:
            return

        # API returns: trades -> tradeCount, shareVolume -> volume, tradeVolume -> turnover
        trade_count = data.get("trades", data.get("tradeCount", "N/A"))
        self.trade_count_label.setText(str(trade_count))

        volume = data.get("shareVolume", data.get("volume", 0))
        if volume >= 1_000_000:
            self.total_volume_label.setText(f"{volume / 1_000_000:.2f}M")
        elif volume >= 1_000:
            self.total_volume_label.setText(f"{volume / 1_000:.2f}K")
        else:
            self.total_volume_label.setText(str(volume))

        turnover = data.get("tradeVolume", data.get("turnover", 0))
        self.total_turnover_label.setText(f"Rs. {turnover:,.0f}")

        # Market breadth will be calculated from stock data
        self.advances_label.setText("Calculating...")
        self.declines_label.setText("Calculating...")
        self.unchanged_label.setText("Calculating...")

    def update_market_breadth(self, data: dict):
        if not data:
            return

        advances = data.get("advances", 0)
        declines = data.get("declines", 0)
        unchanged = data.get("unchanged", 0)
        total = data.get("total", advances + declines + unchanged)

        self.advances_label.setText(
            f"{advances} ({advances / total * 100:.1f}%)" if total > 0 else "0"
        )
        self.declines_label.setText(
            f"{declines} ({declines / total * 100:.1f}%)" if total > 0 else "0"
        )
        self.unchanged_label.setText(
            f"{unchanged} ({unchanged / total * 100:.1f}%)" if total > 0 else "0"
        )

    def update_analytics(self, data: dict):
        if not data:
            return

        # Performance metrics
        perf = data.get("performance", {})
        sentiment = perf.get("market_sentiment", "-")
        sentiment_color = (
            "#00e676"
            if sentiment == "BULLISH"
            else "#f44336"
            if sentiment == "BEARISH"
            else "#e0e0e0"
        )
        self.sentiment_label.setText(
            f"<span style='color: {sentiment_color}'>{sentiment}</span>"
        )

        mean_change = perf.get("mean_change", 0)
        self.mean_change_label.setText(f"{mean_change:+.2f}%")

        positive_ratio = (
            perf.get("positive_count", 0)
            / max(perf.get("positive_count", 1) + perf.get("negative_count", 1), 1)
            * 100
        )
        self.positive_ratio_label.setText(f"{positive_ratio:.1f}%")

        # Momentum
        momentum = data.get("momentum", {})
        mom_dir = momentum.get("momentum_direction", "-")
        self.momentum_label.setText(mom_dir)

        # Price stats
        price = data.get("price", {})
        mean_price = price.get("mean_price", 0)
        self.price_mean_label.setText(f"Rs. {mean_price:,.2f}")

        median_price = price.get("median_price", 0)
        self.price_median_label.setText(f"Rs. {median_price:,.2f}")

        # Volatility
        vol = data.get("volatility", {})
        volatility = vol.get("volatility_percent", 0)
        self.volatility_label.setText(f"{volatility:.2f}%")

        var_95 = vol.get("var_95", 0)
        self.var_label.setText(f"{var_95:+.2f}%")

        # Volume
        volume = data.get("volume", {})
        total_vol = volume.get("total_volume", 0)
        if total_vol >= 1_000_000:
            self.volume_total_label.setText(f"{total_vol / 1_000_000:.2f}M")
        elif total_vol >= 1_000:
            self.volume_total_label.setText(f"{total_vol / 1_000:.2f}K")
        else:
            self.volume_total_label.setText(str(total_vol))

        avg_vol = volume.get("avg_volume", 0)
        if avg_vol >= 1_000_000:
            self.volume_avg_label.setText(f"{avg_vol / 1_000_000:.2f}M")
        elif avg_vol >= 1_000:
            self.volume_avg_label.setText(f"{avg_vol / 1_000:.2f}K")
        else:
            self.volume_avg_label.setText(str(avg_vol))

    def update_gainers(self, gainers: list):
        if not gainers:
            return
        self.top_gainers_table.setRowCount(min(5, len(gainers)))

        for i, g in enumerate(gainers[:5]):
            symbol = g.get("symbol", "-")
            # Handle symbol format like "SHL.N0000" -> "SHL"
            if symbol and ".N" in symbol:
                symbol = symbol.split(".N")[0]

            self.top_gainers_table.setItem(i, 0, QTableWidgetItem(symbol))
            self.top_gainers_table.setItem(
                i, 1, QTableWidgetItem(str(g.get("price", "-")))
            )

            change = g.get(
                "changePercentage",
                g.get("percentageChange", g.get("percentage_change", 0)),
            )
            change_item = QTableWidgetItem(f"+{change:.2f}%")
            change_item.setForeground(Qt.green)
            self.top_gainers_table.setItem(i, 2, change_item)

    def update_losers(self, losers: list):
        if not losers:
            return
        self.top_losers_table.setRowCount(min(5, len(losers)))

        for i, l in enumerate(losers[:5]):
            symbol = l.get("symbol", "-")
            # Handle symbol format like "ODEL.N0000" -> "ODEL"
            if symbol and ".N" in symbol:
                symbol = symbol.split(".N")[0]

            self.top_losers_table.setItem(i, 0, QTableWidgetItem(symbol))
            self.top_losers_table.setItem(
                i, 1, QTableWidgetItem(str(l.get("price", "-")))
            )

            change = l.get(
                "changePercentage",
                l.get("percentageChange", l.get("percentage_change", 0)),
            )
            change_item = QTableWidgetItem(f"{change:.2f}%")
            change_item.setForeground(Qt.red)
            self.top_losers_table.setItem(i, 2, change_item)


class StockComparisonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stocks_data = {}
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("Stock Comparison")
        title.setStyleSheet("""
            QLabel {
                color: #00e676;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(title)

        info = QLabel("Select stocks from the screener to compare their performance")
        info.setStyleSheet("color: #888; font-size: 12px; margin-bottom: 10px;")
        main_layout.addWidget(info)

        toolbar = QHBoxLayout()

        remove_btn = QPushButton("Remove Selected")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: #fff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        remove_btn.clicked.connect(self.remove_selected_stock)

        clear_btn = QPushButton("Clear All")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #444; }
        """)
        clear_btn.clicked.connect(self.clear_all)

        toolbar.addWidget(remove_btn)
        toolbar.addWidget(clear_btn)
        toolbar.addStretch()

        main_layout.addLayout(toolbar)

        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(8)
        self.comparison_table.setHorizontalHeaderLabels(
            [
                "Symbol",
                "Price",
                "Change",
                "Change %",
                "Volume",
                "Turnover",
                "High",
                "Low",
            ]
        )
        self.comparison_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #333;
                gridline-color: #333;
            }
            QTableWidget::item { padding: 10px; }
            QTableWidget::item:selected {
                background-color: #00e676;
                color: #000;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #e0e0e0;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        self.comparison_table.horizontalHeader().setStretchLastSection(True)
        self.comparison_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.comparison_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        main_layout.addWidget(self.comparison_table)

    def add_stock(self, stock_data: dict):
        symbol = stock_data.get("symbol")
        if not symbol or symbol in self.stocks_data:
            return

        self.stocks_data[symbol] = stock_data
        self.update_table()

    def remove_stock(self, symbol: str):
        if symbol in self.stocks_data:
            del self.stocks_data[symbol]
            self.update_table()

    def remove_selected_stock(self):
        current_row = self.comparison_table.currentRow()
        if current_row >= 0:
            symbol = self.comparison_table.item(current_row, 0).text()
            self.remove_stock(symbol)

    def clear_all(self):
        self.stocks_data.clear()
        self.update_table()

    def update_table(self):
        self.comparison_table.setRowCount(len(self.stocks_data))

        for i, (symbol, data) in enumerate(self.stocks_data.items()):
            self.comparison_table.setItem(i, 0, QTableWidgetItem(symbol))
            self.comparison_table.setItem(
                i, 1, QTableWidgetItem(str(data.get("price", "-")))
            )

            change = data.get("change", 0)
            change_item = QTableWidgetItem(f"{change:+.2f}")
            change_item.setForeground(Qt.green if change >= 0 else Qt.red)
            self.comparison_table.setItem(i, 2, change_item)

            pct_change = data.get("percentage_change", 0)
            pct_item = QTableWidgetItem(f"{pct_change:+.2f}%")
            pct_item.setForeground(Qt.green if pct_change >= 0 else Qt.red)
            self.comparison_table.setItem(i, 3, pct_item)

            volume = data.get("volume", 0)
            vol_str = (
                f"{volume / 1_000_000:.2f}M"
                if volume >= 1_000_000
                else f"{volume / 1_000:.1f}K"
            )
            self.comparison_table.setItem(i, 4, QTableWidgetItem(vol_str))

            turnover = data.get("turnover", 0)
            self.comparison_table.setItem(
                i, 5, QTableWidgetItem(f"Rs. {turnover:,.0f}")
            )

            high = data.get("high", "-")
            self.comparison_table.setItem(i, 6, QTableWidgetItem(str(high)))

            low = data.get("low", "-")
            self.comparison_table.setItem(i, 7, QTableWidgetItem(str(low)))
