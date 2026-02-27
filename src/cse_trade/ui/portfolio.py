from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QDialog,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QHeaderView,
    QAbstractItemView,
    QScrollArea,
    QFrame,
    QGroupBox,
    QGridLayout,
    QTabWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor


class AddHoldingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Holding")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(10)

        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("e.g., AAPL")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Company Name (optional)")

        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(99999999)

        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0.01)
        self.price_input.setMaximum(999999.99)
        self.price_input.setDecimals(2)

        layout.addRow("Symbol:", self.symbol_input)
        layout.addRow("Company Name:", self.name_input)
        layout.addRow("Quantity:", self.quantity_input)
        layout.addRow("Avg Price (Rs.):", self.price_input)

        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.accept)

        buttons.addWidget(cancel_btn)
        buttons.addWidget(self.add_btn)

        layout.addRow("", buttons)

    def get_data(self):
        return {
            "symbol": self.symbol_input.text().strip().upper(),
            "company_name": self.name_input.text().strip(),
            "quantity": self.quantity_input.value(),
            "avg_price": self.price_input.value(),
        }


class PortfolioWidget(QWidget):
    holding_selected = Signal(str)
    watchlist_updated = Signal()

    def __init__(self, portfolio_manager, parent=None):
        super().__init__(parent)
        self.portfolio = portfolio_manager
        self.stock_prices = {}
        self.setup_ui()
        self.load_data()

    def set_stock_prices(self, prices: dict):
        self.stock_prices = prices
        self.update_portfolio_values()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        summary_group = self._create_summary_group()
        main_layout.addWidget(summary_group)

        tabs = QTabWidget()

        holdings_tab = self._create_holdings_tab()
        tabs.addTab(holdings_tab, "Holdings")

        watchlist_tab = self._create_watchlist_tab()
        tabs.addTab(watchlist_tab, "Watchlist")

        transactions_tab = self._create_transactions_tab()
        tabs.addTab(transactions_tab, "Transactions")

        main_layout.addWidget(tabs)

    def _create_summary_group(self) -> QGroupBox:
        group = QGroupBox("Portfolio Summary")
        group.setStyleSheet("""
            QGroupBox {
                color: #00e676;
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

        self.total_invested_label = QLabel("Rs. 0.00")
        self.total_invested_label.setStyleSheet("color: #e0e0e0; font-size: 18px;")

        self.total_value_label = QLabel("Rs. 0.00")
        self.total_value_label.setStyleSheet(
            "color: #00e676; font-size: 18px; font-weight: bold;"
        )

        self.total_pnl_label = QLabel("Rs. 0.00 (0.00%)")
        self.total_pnl_label.setStyleSheet("color: #e0e0e0; font-size: 16px;")

        self.holdings_count_label = QLabel("0 Holdings")
        self.holdings_count_label.setStyleSheet("color: #888;")

        layout.addWidget(QLabel("Total Invested:"), 0, 0)
        layout.addWidget(self.total_invested_label, 0, 1)
        layout.addWidget(QLabel("Current Value:"), 0, 2)
        layout.addWidget(self.total_value_label, 0, 3)
        layout.addWidget(QLabel("Total P&L:"), 1, 0)
        layout.addWidget(self.total_pnl_label, 1, 1)
        layout.addWidget(QLabel("Holdings:"), 1, 2)
        layout.addWidget(self.holdings_count_label, 1, 3)

        group.setLayout(layout)
        return group

    def _create_holdings_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()

        add_btn = QPushButton("+ Add Holding")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #00e676;
                color: #000;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00c853; }
        """)
        add_btn.clicked.connect(self.add_holding)

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
        remove_btn.clicked.connect(self.remove_holding)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #444; }
        """)
        refresh_btn.clicked.connect(self.load_data)

        clear_btn = QPushButton("Clear All")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: #fff;
                border: 1px solid #f44336;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        clear_btn.clicked.connect(self.clear_all_holdings)

        toolbar.addWidget(add_btn)
        toolbar.addWidget(remove_btn)
        toolbar.addWidget(clear_btn)
        toolbar.addStretch()
        toolbar.addWidget(refresh_btn)

        layout.addLayout(toolbar)

        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(8)
        self.holdings_table.setHorizontalHeaderLabels(
            [
                "Symbol",
                "Name",
                "Qty",
                "Avg Price",
                "Current Price",
                "Value",
                "P&L",
                "P&L %",
            ]
        )
        self.holdings_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #333;
                gridline-color: #333;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #00e676;
                color: #000;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #e0e0e0;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.holdings_table.horizontalHeader().setStretchLastSection(True)
        self.holdings_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.holdings_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addWidget(self.holdings_table)

        return widget

    def _create_watchlist_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()

        add_watch_btn = QPushButton("+ Add to Watchlist")
        add_watch_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: #fff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976d2; }
        """)
        add_watch_btn.clicked.connect(self.add_to_watchlist)

        remove_watch_btn = QPushButton("Remove Selected")
        remove_watch_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: #fff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        remove_watch_btn.clicked.connect(self.remove_from_watchlist)

        clear_watch_btn = QPushButton("Clear All")
        clear_watch_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: #fff;
                border: 1px solid #f44336;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        clear_watch_btn.clicked.connect(self.clear_all_watchlist)

        toolbar.addWidget(add_watch_btn)
        toolbar.addWidget(remove_watch_btn)
        toolbar.addWidget(clear_watch_btn)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        self.watchlist_table = QTableWidget()
        self.watchlist_table.setColumnCount(5)
        self.watchlist_table.setHorizontalHeaderLabels(
            ["Symbol", "Company", "Current Price", "Target Price", "Status"]
        )
        self.watchlist_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #333;
                gridline-color: #333;
            }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected { background-color: #2196f3; color: #fff; }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #e0e0e0;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.watchlist_table.horizontalHeader().setStretchLastSection(True)
        self.watchlist_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.watchlist_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addWidget(self.watchlist_table)

        return widget

    def _create_transactions_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()

        add_buy_btn = QPushButton("+ Record Buy")
        add_buy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: #fff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #388e3c; }
        """)
        add_buy_btn.clicked.connect(lambda: self.record_transaction("BUY"))

        add_sell_btn = QPushButton("+ Record Sell")
        add_sell_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: #fff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        add_sell_btn.clicked.connect(lambda: self.record_transaction("SELL"))

        remove_trans_btn = QPushButton("Remove Selected")
        remove_trans_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: #fff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #f57c00; }
        """)
        remove_trans_btn.clicked.connect(self.remove_transaction)

        clear_trans_btn = QPushButton("Clear All")
        clear_trans_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #444; }
        """)
        clear_trans_btn.clicked.connect(self.clear_all_transactions)

        toolbar.addWidget(add_buy_btn)
        toolbar.addWidget(add_sell_btn)
        toolbar.addWidget(remove_trans_btn)
        toolbar.addWidget(clear_trans_btn)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(
            ["Date", "Symbol", "Type", "Qty", "Price", "Total"]
        )
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #333;
                gridline-color: #333;
            }
            QTableWidget::item { padding: 8px; }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #e0e0e0;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        self.transactions_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addWidget(self.transactions_table)

        return widget

    def load_data(self):
        holdings = self.portfolio.get_holdings()

        self.holdings_table.setRowCount(len(holdings))

        for i, h in enumerate(holdings):
            current_price = self.stock_prices.get(h["symbol"], h["avg_price"])
            value = h["quantity"] * current_price
            invested = h["quantity"] * h["avg_price"]
            pnl = value - invested
            pnl_pct = (pnl / invested * 100) if invested > 0 else 0

            self.holdings_table.setItem(i, 0, QTableWidgetItem(h["symbol"]))
            self.holdings_table.setItem(
                i, 1, QTableWidgetItem(h.get("company_name", "-"))
            )
            self.holdings_table.setItem(i, 2, QTableWidgetItem(str(h["quantity"])))
            self.holdings_table.setItem(
                i, 3, QTableWidgetItem(f"Rs. {h['avg_price']:.2f}")
            )
            self.holdings_table.setItem(
                i, 4, QTableWidgetItem(f"Rs. {current_price:.2f}")
            )
            self.holdings_table.setItem(i, 5, QTableWidgetItem(f"Rs. {value:.2f}"))

            pnl_item = QTableWidgetItem(f"Rs. {pnl:.2f}")
            pnl_item.setForeground(QColor("#4caf50" if pnl >= 0 else "#f44336"))
            self.holdings_table.setItem(i, 6, pnl_item)

            pnl_pct_item = QTableWidgetItem(f"{pnl_pct:.2f}%")
            pnl_pct_item.setForeground(QColor("#4caf50" if pnl_pct >= 0 else "#f44336"))
            self.holdings_table.setItem(i, 7, pnl_pct_item)

        watchlist = self.portfolio.get_watchlist()

        self.watchlist_table.setRowCount(len(watchlist))

        for i, w in enumerate(watchlist):
            current_price = self.stock_prices.get(w["symbol"], 0)
            target = w.get("target_price")

            status = "-"
            if target and current_price:
                if current_price <= target:
                    status = "✓ Below Target"
                else:
                    status = "↑ Above Target"

            self.watchlist_table.setItem(i, 0, QTableWidgetItem(w["symbol"]))
            self.watchlist_table.setItem(
                i, 1, QTableWidgetItem(w.get("company_name", "-"))
            )
            self.watchlist_table.setItem(
                i,
                2,
                QTableWidgetItem(f"Rs. {current_price:.2f}" if current_price else "-"),
            )
            self.watchlist_table.setItem(
                i, 3, QTableWidgetItem(f"Rs. {target:.2f}" if target else "-")
            )
            self.watchlist_table.setItem(i, 4, QTableWidgetItem(status))

        transactions = self.portfolio.get_transactions()

        self.transactions_table.setRowCount(len(transactions))

        for i, t in enumerate(transactions):
            self.transactions_table.setItem(
                i, 0, QTableWidgetItem(t.get("transaction_date", "-"))
            )
            self.transactions_table.setItem(i, 1, QTableWidgetItem(t["symbol"]))

            type_item = QTableWidgetItem(t["transaction_type"])
            type_item.setForeground(
                QColor("#4caf50" if t["transaction_type"] == "BUY" else "#f44336")
            )
            self.transactions_table.setItem(i, 2, type_item)

            self.transactions_table.setItem(i, 3, QTableWidgetItem(str(t["quantity"])))
            self.transactions_table.setItem(
                i, 4, QTableWidgetItem(f"Rs. {t['price']:.2f}")
            )
            self.transactions_table.setItem(
                i, 5, QTableWidgetItem(f"Rs. {t['total']:.2f}")
            )

        self.update_portfolio_values()

    def update_portfolio_values(self):
        data = self.portfolio.get_portfolio_value(self.stock_prices)

        self.total_invested_label.setText(f"Rs. {data['total_invested']:,.2f}")
        self.total_value_label.setText(f"Rs. {data['total_current']:,.2f}")

        pnl_color = "#4caf50" if data["total_pnl"] >= 0 else "#f44336"
        self.total_pnl_label.setText(
            f"<span style='color: {pnl_color}'>Rs. {data['total_pnl']:,.2f} ({data['total_pnl_pct']:.2f}%)</span>"
        )

        self.holdings_count_label.setText(f"{len(data['holdings'])} Holdings")

        for i, h in enumerate(data["holdings"]):
            if i < self.holdings_table.rowCount():
                self.holdings_table.setItem(
                    i, 4, QTableWidgetItem(f"Rs. {h['current_price']:.2f}")
                )
                self.holdings_table.setItem(
                    i, 5, QTableWidgetItem(f"Rs. {h['current_value']:.2f}")
                )

                pnl_item = QTableWidgetItem(f"Rs. {h['pnl']:.2f}")
                pnl_item.setForeground(
                    QColor("#4caf50" if h["pnl"] >= 0 else "#f44336")
                )
                self.holdings_table.setItem(i, 6, pnl_item)

                pnl_pct_item = QTableWidgetItem(f"{h['pnl_pct']:.2f}%")
                pnl_pct_item.setForeground(
                    QColor("#4caf50" if h["pnl_pct"] >= 0 else "#f44336")
                )
                self.holdings_table.setItem(i, 7, pnl_pct_item)

    def add_holding(self):
        dialog = AddHoldingDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data["symbol"]:
                self.portfolio.add_holding(
                    data["symbol"],
                    data["quantity"],
                    data["avg_price"],
                    data["company_name"],
                )
                self.load_data()
                self.watchlist_updated.emit()

    def remove_holding(self):
        current_row = self.holdings_table.currentRow()
        if current_row >= 0:
            symbol = self.holdings_table.item(current_row, 0).text()
            holdings = self.portfolio.get_holdings()
            for h in holdings:
                if h["symbol"] == symbol:
                    self.portfolio.remove_holding(h["id"])
                    break
            self.load_data()

    def clear_all_holdings(self):
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Clear All Holdings",
            "Are you sure you want to delete all holdings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.portfolio.clear_all_holdings()
            self.load_data()

    def add_to_watchlist(self):
        from PySide6.QtWidgets import QInputDialog

        symbol, ok = QInputDialog.getText(
            self, "Add to Watchlist", "Enter Stock Symbol:"
        )
        if ok and symbol.strip():
            self.portfolio.add_to_watchlist(symbol.strip().upper())
            self.load_data()
            self.watchlist_updated.emit()

    def remove_from_watchlist(self):
        current_row = self.watchlist_table.currentRow()
        if current_row >= 0:
            symbol = self.watchlist_table.item(current_row, 0).text()
            self.portfolio.remove_from_watchlist(symbol)
            self.load_data()
            self.watchlist_updated.emit()

    def clear_all_watchlist(self):
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Clear Watchlist",
            "Are you sure you want to delete all stocks from watchlist?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.portfolio.clear_all_watchlist()
            self.load_data()
            self.watchlist_updated.emit()

    def record_transaction(self, trans_type: str):
        dialog = AddHoldingDialog(self)
        dialog.setWindowTitle(f"Record {trans_type}")
        if dialog.exec():
            data = dialog.get_data()
            if data["symbol"]:
                total = data["quantity"] * data["avg_price"]
                self.portfolio.add_transaction(
                    data["symbol"],
                    trans_type,
                    data["quantity"],
                    data["avg_price"],
                    total,
                )
                self.load_data()

    def remove_transaction(self):
        current_row = self.transactions_table.currentRow()
        if current_row >= 0:
            # Get all transactions, rebuild excluding the selected one
            transactions = self.portfolio.get_transactions()
            if transactions:
                # Clear all and rebuild
                self.portfolio.clear_all_transactions()
                # Remove the selected row from our temp list
                # We identify by row position since there's no unique ID in display
                for i, t in enumerate(transactions):
                    if i != current_row:
                        self.portfolio.add_transaction(
                            t.get("symbol"),
                            t.get("transaction_type"),
                            t.get("quantity"),
                            t.get("price"),
                            t.get("total"),
                        )
                self.load_data()

    def clear_all_transactions(self):
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Clear All Transactions",
            "Are you sure you want to delete all transactions?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.portfolio.clear_all_transactions()
            self.load_data()

    def clear_all_transactions(self):
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Clear All Transactions",
            "Are you sure you want to delete all transactions?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.portfolio.clear_all_transactions()
            self.load_data()
