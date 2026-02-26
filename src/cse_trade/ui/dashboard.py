from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Indices Section
        indices_layout = QHBoxLayout()
        self.aspi_card = self.create_index_card("ASPI", "0.00", "0.00 (0.00%)")
        self.snp_card = self.create_index_card("S&P SL20", "0.00", "0.00 (0.00%)")
        indices_layout.addWidget(self.aspi_card)
        indices_layout.addWidget(self.snp_card)
        layout.addLayout(indices_layout)

        # Gainers and Losers Section
        gl_layout = QHBoxLayout()
        self.gainers_container, self.gainers_qtable = self.create_stock_table("Top Gainers", "#00e676")
        self.losers_container, self.losers_qtable = self.create_stock_table("Top Losers", "#ff5252")
        gl_layout.addWidget(self.gainers_container)
        gl_layout.addWidget(self.losers_container)
        layout.addLayout(gl_layout)

        layout.addStretch()

    def create_index_card(self, title, value, change):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("background-color: #1e1e1e; border-radius: 8px; padding: 15px; border: 1px solid #333;")
        
        layout = QVBoxLayout(card)
        
        # Store references for direct update
        val_label = QLabel(value)
        val_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; border: none;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #b0b0b0; font-size: 14px; border: none;")
        
        chg_label = QLabel(change)
        chg_label.setStyleSheet("font-size: 14px; border: none;")
        
        # Map them by index names to attributes for easy access
        attr_prefix = title.lower().replace(" ", "_").replace("&", "").replace("-", "")
        setattr(self, f"{attr_prefix}_val_lbl", val_label)
        setattr(self, f"{attr_prefix}_chg_lbl", chg_label)
        
        layout.addWidget(title_label)
        layout.addWidget(val_label)
        layout.addWidget(chg_label)
        return card

    def create_stock_table(self, title, color):
        container = QFrame()
        container.setStyleSheet(f"background-color: #1e1e1e; border-radius: 8px; border: 1px solid {color};")
        layout = QVBoxLayout(container)
        
        label = QLabel(title)
        label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold; border: none; padding: 5px;")
        layout.addWidget(label)
        
        table = QTableWidget(0, 2)
        table.setHorizontalHeaderLabels(["Symbol", "Change %"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                gridline-color: transparent;
                border: none;
                color: white;
            }}
            QHeaderView::section {{
                background-color: #252525;
                color: #b0b0b0;
                padding: 5px;
                border: none;
            }}
        """)
        
        layout.addWidget(table)
        return container, table

    def update_indices(self, aspi_data, snp_data):
        if aspi_data:
            val = aspi_data.get('value', '0.00')
            chg = aspi_data.get('change', '0.00')
            pct = aspi_data.get('percentage', '0.00')
            self.aspi_val_lbl.setText(str(val))
            self.aspi_chg_lbl.setText(f"{chg} ({float(pct):.2f}%)")
            try:
                self.aspi_chg_lbl.setStyleSheet(f"color: {'#00e676' if float(chg) >= 0 else '#ff5252'}; border: none;")
            except: pass

        if snp_data:
            val = snp_data.get('value', '0.00')
            chg = snp_data.get('change', '0.00')
            pct = snp_data.get('percentage', '0.00')
            self.sp_sl20_val_lbl.setText(str(val))
            self.sp_sl20_chg_lbl.setText(f"{chg} ({float(pct):.2f}%)")
            try:
                self.sp_sl20_chg_lbl.setStyleSheet(f"color: {'#00e676' if float(chg) >= 0 else '#ff5252'}; border: none;")
            except: pass

    def update_gainers_losers(self, gainers, losers):
        if hasattr(self, 'gainers_qtable'):
            self._populate_table(self.gainers_qtable, gainers, "#00e676")
        if hasattr(self, 'losers_qtable'):
            self._populate_table(self.losers_qtable, losers, "#ff5252")

    def _populate_table(self, table, stocks, color):
        if not table: return
        table.setRowCount(0)
        if not stocks:
            return
            
        for stock in stocks[:10]:
            row = table.rowCount()
            table.insertRow(row)
            
            sym_item = QTableWidgetItem(stock.get('symbol', ''))
            sym_item.setForeground(Qt.white)
            sym_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # handle both changePercentage and percentageChange
            pct_val = stock.get('changePercentage', stock.get('percentageChange', '0.0'))
            try:
                chg_item = QTableWidgetItem(f"{float(pct_val):.2f}%")
            except:
                chg_item = QTableWidgetItem(f"{pct_val}%")
            
            chg_item.setForeground(QColor(color))
            chg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            table.setItem(row, 0, sym_item)
            table.setItem(row, 1, chg_item)
