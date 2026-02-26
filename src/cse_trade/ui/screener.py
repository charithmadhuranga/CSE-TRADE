from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QTableView, QPushButton, QLabel)
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem

class StockScreenerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Search and Filter
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Symbol or Company Name...")
        self.search_input.setStyleSheet("padding: 8px; background-color: #1e1e1e; color: white; border-radius: 4px;")
        self.search_input.textChanged.connect(self.filter_data)
        
        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.setStyleSheet("background-color: #00e676; color: black; font-weight: bold; padding: 8px;")
        
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.export_btn)
        layout.addLayout(top_layout)

        # Table
        self.model = QStandardItemModel(0, 7)
        self.model.setHorizontalHeaderLabels([
            "Symbol", "Name", "Price", "Change", "% Change", "Volume", "Turnover"
        ])
        
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1) # Filter across all columns
        
        self.table = QTableView()
        self.table.setModel(self.proxy_model)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet("""
            QTableView {
                background-color: #121212;
                color: white;
                gridline-color: #333;
                border: none;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #b0b0b0;
                padding: 10px;
                border: 1px solid #333;
            }
        """)
        
        layout.addWidget(self.table)

    def filter_data(self, text):
        self.proxy_model.setFilterFixedString(text)

    def update_table(self, data):
        self.model.setRowCount(0)
        
        # Handle dict-wrapped list from tradeSummary
        if isinstance(data, dict) and 'reqTradeSummery' in data:
            stock_list = data['reqTradeSummery']
        elif isinstance(data, list):
            stock_list = data
        else:
            return
            
        for stock in stock_list:
            if not isinstance(stock, dict):
                row = [QStandardItem(str(stock))] + [QStandardItem("") for _ in range(6)]
            else:
                # Map keys based on actual API response structure
                row = [
                    QStandardItem(str(stock.get('symbol', ''))),
                    QStandardItem(str(stock.get('name', ''))),
                    QStandardItem(str(stock.get('price', stock.get('lastTradedPrice', '0.0')))),
                    QStandardItem(str(stock.get('change', '0.0'))),
                    QStandardItem(str(stock.get('percentageChange', stock.get('changePercentage', '0.0')))),
                    QStandardItem(str(stock.get('sharevolume', stock.get('volume', '0')))),
                    QStandardItem(str(stock.get('turnover', '0.0')))
                ]
            self.model.appendRow(row)
