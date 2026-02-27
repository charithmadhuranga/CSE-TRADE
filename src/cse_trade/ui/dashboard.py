from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGridLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Indices Section
        indices_layout = QHBoxLayout()
        self.aspi_card = self.create_index_card("ASPI", "0.00", "0.00 (0.00%)")
        self.snp_card = self.create_index_card("S&P SL20", "0.00", "0.00 (0.00%)")
        indices_layout.addWidget(self.aspi_card)
        indices_layout.addWidget(self.snp_card)
        layout.addLayout(indices_layout)

        # Market Summary Section
        summary_layout = QHBoxLayout()
        self.trade_count_card = self.create_summary_card("Trade Count", "0")
        self.volume_card = self.create_summary_card("Total Volume", "0")
        self.turnover_card = self.create_summary_card("Turnover", "Rs. 0")
        self.market_sentiment_card = self.create_summary_card("Sentiment", "-")
        summary_layout.addWidget(self.trade_count_card)
        summary_layout.addWidget(self.volume_card)
        summary_layout.addWidget(self.turnover_card)
        summary_layout.addWidget(self.market_sentiment_card)
        layout.addLayout(summary_layout)

        # Market Breadth Section
        breadth_layout = QHBoxLayout()
        self.advances_card = self.create_breadth_card("Advances", "0", "#00e676")
        self.declines_card = self.create_breadth_card("Declines", "0", "#ff5252")
        self.unchanged_card = self.create_breadth_card("Unchanged", "0", "#ff9800")
        breadth_layout.addWidget(self.advances_card)
        breadth_layout.addWidget(self.declines_card)
        breadth_layout.addWidget(self.unchanged_card)
        layout.addLayout(breadth_layout)

        # Gainers, Losers, Most Active Section
        gl_layout = QHBoxLayout()

        # Top Gainers
        gainer_container = QFrame()
        gainer_container.setStyleSheet(
            "background-color: #1e1e1e; border-radius: 8px; border: 1px solid #00e676;"
        )
        gainer_vbox = QVBoxLayout(gainer_container)
        gainer_label = QLabel("Top Gainers ▲")
        gainer_label.setStyleSheet(
            "color: #00e676; font-size: 16px; font-weight: bold; padding: 8px;"
        )
        gainer_vbox.addWidget(gainer_label)

        self.gainers_qtable = QTableWidget(0, 2)
        self.gainers_qtable.setHorizontalHeaderLabels(["Symbol", "Change %"])
        self.gainers_qtable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.gainers_qtable.verticalHeader().setVisible(False)
        self.gainers_qtable.setShowGrid(False)
        self.gainers_qtable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gainers_qtable.setSelectionMode(QTableWidget.NoSelection)
        self.gainers_qtable.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                gridline-color: transparent;
                border: none;
                color: white;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #b0b0b0;
                padding: 5px;
                border: none;
            }
        """)
        gainer_vbox.addWidget(self.gainers_qtable)

        # Top Losers
        loser_container = QFrame()
        loser_container.setStyleSheet(
            "background-color: #1e1e1e; border-radius: 8px; border: 1px solid #ff5252;"
        )
        loser_vbox = QVBoxLayout(loser_container)
        loser_label = QLabel("Top Losers ▼")
        loser_label.setStyleSheet(
            "color: #ff5252; font-size: 16px; font-weight: bold; padding: 8px;"
        )
        loser_vbox.addWidget(loser_label)

        self.losers_qtable = QTableWidget(0, 2)
        self.losers_qtable.setHorizontalHeaderLabels(["Symbol", "Change %"])
        self.losers_qtable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.losers_qtable.verticalHeader().setVisible(False)
        self.losers_qtable.setShowGrid(False)
        self.losers_qtable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.losers_qtable.setSelectionMode(QTableWidget.NoSelection)
        self.losers_qtable.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                gridline-color: transparent;
                border: none;
                color: white;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #b0b0b0;
                padding: 5px;
                border: none;
            }
        """)
        loser_vbox.addWidget(self.losers_qtable)

        # Most Active by Volume
        active_container = QFrame()
        active_container.setStyleSheet(
            "background-color: #1e1e1e; border-radius: 8px; border: 1px solid #2196f3;"
        )
        active_vbox = QVBoxLayout(active_container)
        active_label = QLabel("Most Active by Volume 🔊")
        active_label.setStyleSheet(
            "color: #2196f3; font-size: 16px; font-weight: bold; padding: 8px;"
        )
        active_vbox.addWidget(active_label)

        self.active_qtable = QTableWidget(0, 3)
        self.active_qtable.setHorizontalHeaderLabels(["Symbol", "Volume", "Price"])
        self.active_qtable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.active_qtable.verticalHeader().setVisible(False)
        self.active_qtable.setShowGrid(False)
        self.active_qtable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.active_qtable.setSelectionMode(QTableWidget.NoSelection)
        self.active_qtable.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                gridline-color: transparent;
                border: none;
                color: white;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #b0b0b0;
                padding: 5px;
                border: none;
            }
        """)
        active_vbox.addWidget(self.active_qtable)

        gl_layout.addWidget(gainer_container, 1)
        gl_layout.addWidget(loser_container, 1)
        gl_layout.addWidget(active_container, 1)
        layout.addLayout(gl_layout)

        layout.addStretch()

    def create_index_card(self, title, value, change):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(
            "background-color: #1e1e1e; border-radius: 8px; padding: 15px; border: 1px solid #333;"
        )

        layout = QVBoxLayout(card)

        val_label = QLabel(value)
        val_label.setStyleSheet(
            "color: white; font-size: 24px; font-weight: bold; border: none;"
        )

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #b0b0b0; font-size: 14px; border: none;")

        chg_label = QLabel(change)
        chg_label.setStyleSheet("font-size: 14px; border: none;")

        attr_prefix = title.lower().replace(" ", "_").replace("&", "").replace("-", "")
        setattr(self, f"{attr_prefix}_val_lbl", val_label)
        setattr(self, f"{attr_prefix}_chg_lbl", chg_label)

        layout.addWidget(title_label)
        layout.addWidget(val_label)
        layout.addWidget(chg_label)
        return card

    def create_summary_card(self, title, value):
        card = QFrame()
        card.setStyleSheet(
            "background-color: #252525; border-radius: 6px; padding: 10px; border: 1px solid #333;"
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(5, 5, 5, 5)

        val_label = QLabel(value)
        val_label.setStyleSheet(
            "color: #00e676; font-size: 16px; font-weight: bold; border: none;"
        )

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888; font-size: 11px; border: none;")

        attr_name = title.lower().replace(" ", "_")
        setattr(self, f"summary_{attr_name}_lbl", val_label)

        layout.addWidget(title_label)
        layout.addWidget(val_label)
        return card

    def create_breadth_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(
            f"background-color: #252525; border-radius: 6px; padding: 10px; border: 1px solid {color};"
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(5, 5, 5, 5)

        val_label = QLabel(value)
        val_label.setStyleSheet(
            f"color: {color}; font-size: 18px; font-weight: bold; border: none;"
        )

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888; font-size: 11px; border: none;")

        attr_name = title.lower()
        setattr(self, f"breadth_{attr_name}_lbl", val_label)

        layout.addWidget(title_label)
        layout.addWidget(val_label)
        return card

    def update_indices(self, aspi_data, snp_data):
        if aspi_data:
            val = aspi_data.get("value", "0.00")
            chg = aspi_data.get("change", "0.00")
            pct = aspi_data.get("percentage", "0.00")
            self.aspi_val_lbl.setText(str(val))
            self.aspi_chg_lbl.setText(f"{chg} ({float(pct):.2f}%)")
            try:
                self.aspi_chg_lbl.setStyleSheet(
                    f"color: {'#00e676' if float(chg) >= 0 else '#ff5252'}; border: none;"
                )
            except:
                pass

        if snp_data:
            val = snp_data.get("value", "0.00")
            chg = snp_data.get("change", "0.00")
            pct = snp_data.get("percentage", "0.00")
            self.sp_sl20_val_lbl.setText(str(val))
            self.sp_sl20_chg_lbl.setText(f"{chg} ({float(pct):.2f}%)")
            try:
                self.sp_sl20_chg_lbl.setStyleSheet(
                    f"color: {'#00e676' if float(chg) >= 0 else '#ff5252'}; border: none;"
                )
            except:
                pass

    def update_market_summary(self, data):
        if not data:
            return

        # Trade Count
        trades = data.get("trades", 0)
        self.summary_trade_count_lbl.setText(f"{trades:,}")

        # Volume
        volume = data.get("shareVolume", 0)
        if volume >= 1_000_000:
            self.summary_total_volume_lbl.setText(f"{volume / 1_000_000:.2f}M")
        elif volume >= 1_000:
            self.summary_total_volume_lbl.setText(f"{volume / 1_000:.2f}K")
        else:
            self.summary_total_volume_lbl.setText(str(volume))

        # Turnover
        turnover = data.get("tradeVolume", 0)
        if turnover >= 1_000_000_000:
            self.summary_turnover_lbl.setText(f"Rs. {turnover / 1_000_000_000:.2f}B")
        elif turnover >= 1_000_000:
            self.summary_turnover_lbl.setText(f"Rs. {turnover / 1_000_000:.2f}M")
        else:
            self.summary_turnover_lbl.setText(f"Rs. {turnover:,.0f}")

    def update_breadth(self, advances, declines, unchanged, sentiment):
        total = advances + declines + unchanged

        self.breadth_advances_lbl.setText(
            f"{advances} ({advances / total * 100:.1f}%)" if total > 0 else "0"
        )
        self.breadth_declines_lbl.setText(
            f"{declines} ({declines / total * 100:.1f}%)" if total > 0 else "0"
        )
        self.breadth_unchanged_lbl.setText(
            f"{unchanged} ({unchanged / total * 100:.1f}%)" if total > 0 else "0"
        )

        sentiment_color = (
            "#00e676"
            if sentiment == "BULLISH"
            else "#ff5252"
            if sentiment == "BEARISH"
            else "#ff9800"
        )
        self.summary_sentiment_lbl.setText(
            f"<span style='color: {sentiment_color}'>{sentiment}</span>"
        )

    def update_gainers_losers(self, gainers, losers):
        if hasattr(self, "gainers_qtable"):
            self._populate_table(self.gainers_qtable, gainers, "#00e676")
        if hasattr(self, "losers_qtable"):
            self._populate_table(self.losers_qtable, losers, "#ff5252")

    def update_most_active(self, stocks):
        if not hasattr(self, "active_qtable") or not stocks:
            return

        table = self.active_qtable
        table.setRowCount(0)

        # Sort by volume and get top 10
        sorted_stocks = sorted(
            stocks,
            key=lambda x: x.get("tradevolume", x.get("sharevolume", 0)),
            reverse=True,
        )[:10]

        for stock in sorted_stocks:
            row = table.rowCount()
            table.insertRow(row)

            symbol = stock.get("symbol", "")
            if ".N" in symbol:
                symbol = symbol.split(".N")[0]

            sym_item = QTableWidgetItem(symbol)
            sym_item.setForeground(Qt.white)
            sym_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            volume = stock.get("tradevolume", stock.get("sharevolume", 0))
            vol_str = (
                f"{volume / 1_000_000:.2f}M"
                if volume >= 1_000_000
                else f"{volume / 1_000:.1f}K"
            )
            vol_item = QTableWidgetItem(vol_str)
            vol_item.setForeground(Qt.cyan)
            vol_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            price = stock.get("price", "-")
            price_item = QTableWidgetItem(f"Rs. {price}")
            price_item.setForeground(Qt.white)
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            table.setItem(row, 0, sym_item)
            table.setItem(row, 1, vol_item)
            table.setItem(row, 2, price_item)

    def _populate_table(self, table, stocks, color):
        if not table:
            return
        table.setRowCount(0)
        if not stocks:
            return

        for stock in stocks[:10]:
            row = table.rowCount()
            table.insertRow(row)

            sym_item = QTableWidgetItem(stock.get("symbol", ""))
            sym_item.setForeground(Qt.white)
            sym_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            pct_val = stock.get(
                "changePercentage", stock.get("percentageChange", "0.0")
            )
            try:
                chg_item = QTableWidgetItem(f"{float(pct_val):.2f}%")
            except:
                chg_item = QTableWidgetItem(f"{pct_val}%")

            chg_item.setForeground(QColor(color))
            chg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            table.setItem(row, 0, sym_item)
            table.setItem(row, 1, chg_item)
