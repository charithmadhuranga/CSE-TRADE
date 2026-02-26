import pyqtgraph as pg
import pandas as pd
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from PySide6.QtCore import Qt

class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.symbol_label = QLabel("Select a stock from the screener")
        self.symbol_label.setStyleSheet("color: #00e676; font-size: 16px; font-weight: bold;")
        
        self.timeframe_selector = QComboBox()
        self.timeframe_selector.addItems(["1D", "5D", "1M", "1Y"])
        self.timeframe_selector.setStyleSheet("background-color: #1e1e1e; color: white; padding: 5px;")
        
        controls_layout.addWidget(self.symbol_label)
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("Timeframe:"))
        controls_layout.addWidget(self.timeframe_selector)
        layout.addLayout(controls_layout)

        # Plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#121212')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.getAxis('left').setPen('#b0b0b0')
        self.plot_widget.getAxis('bottom').setPen('#b0b0b0')
        
        # Optimization for stability and performance
        self.plot_widget.setDownsampling(auto=True, mode='peak')
        self.plot_widget.setClipToView(True)
        
        # Persistent plot item
        self.line_plot = self.plot_widget.plot(pen=pg.mkPen(color='#00e676', width=2))
        
        layout.addWidget(self.plot_widget)

        # Analytics Panel
        self.analytics_panel = QHBoxLayout()
        self.rsi_label = QLabel("RSI: --")
        self.sma_label = QLabel("SMA (20): --")
        self.vol_label = QLabel("Volatility: --")
        
        for lbl in [self.rsi_label, self.sma_label, self.vol_label]:
            lbl.setStyleSheet("color: #b0b0b0; font-size: 12px;")
            self.analytics_panel.addWidget(lbl)
        
        layout.addLayout(self.analytics_panel)

    def update_chart(self, df):
        if df.empty:
            self.symbol_label.setText("No chart data available for this selection")
            self.symbol_label.setStyleSheet("color: #ff5252; font-size: 16px; font-weight: bold;")
            self.line_plot.setData([], [])
            return
        
        try:
            import numpy as np
            self.symbol_label.setStyleSheet("color: #00e676; font-size: 16px; font-weight: bold;")
            
            if 'y_price' in df.columns:
                y = df['y_price'].to_numpy(dtype='float64')
            else:
                # Fallback
                price_col = 'lastTradedPrice' if 'lastTradedPrice' in df.columns else (
                            'price' if 'price' in df.columns else df.columns[-1])
                y = pd.to_numeric(df[price_col], errors='coerce').ffill().bfill().to_numpy(dtype='float64')
            
            # Manual downsampling for very large datasets to keep UI snappy
            if len(y) > 5000:
                # Keep local peaks (min/max) for visual accuracy
                step = len(y) // 2500
                y = y[::step]
            
            x = np.arange(len(y), dtype='float64')
            
            # Efficient update
            self.line_plot.setData(x, y)
            self.plot_widget.autoRange() # Ensure data is visible
            
            # Indicators
            from ..core.models import AnalyticsEngine
            prices = pd.Series(y)
            
            if len(prices) >= 20:
                sma_series = AnalyticsEngine.calculate_sma(prices)
                sma = sma_series.iloc[-1]
                if not pd.isna(sma):
                    self.sma_label.setText(f"SMA (20): {sma:.2f}")
                else:
                    self.sma_label.setText("SMA (20): --")
            else:
                self.sma_label.setText("SMA (20): N/A (Need 20 points)")

            if len(prices) >= 15:
                rsi_series = AnalyticsEngine.calculate_rsi(prices)
                rsi = rsi_series.iloc[-1]
                if not pd.isna(rsi):
                    self.rsi_label.setText(f"RSI (14): {rsi:.2f}")
                    # Conditional coloring for RSI
                    if rsi > 70: self.rsi_label.setStyleSheet("color: #ff5252;")
                    elif rsi < 30: self.rsi_label.setStyleSheet("color: #00e676;")
                    else: self.rsi_label.setStyleSheet("color: #b0b0b0;")
                else:
                    self.rsi_label.setText("RSI (14): --")
            else:
                self.rsi_label.setText("RSI (14): N/A (Need 15 points)")
            
            if len(prices) >= 2:
                vol = AnalyticsEngine.calculate_volatility(prices)
                if not pd.isna(vol):
                    self.vol_label.setText(f"Volatility: {vol:.2%}")
                else:
                    self.vol_label.setText("Volatility: --")
            else:
                self.vol_label.setText("Volatility: N/A")
            
        except Exception as e:
            print(f"Chart Render Error: {e}")
