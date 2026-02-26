import sys
import pandas as pd
import logging
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QStatusBar, QProgressBar, QApplication,
                             QTabWidget, QLabel, QPushButton)
from PySide6.QtCore import Qt, QThreadPool, QObject, Signal, Slot, QThread, QTimer

# Setup logging
logging.basicConfig(
    filename='/tmp/cse_trade.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from ..api.client import CSEClient
from ..ui.dashboard import DashboardWidget
from ..ui.screener import StockScreenerWidget
from ..ui.charts import ChartWidget
from ..threads.workers import Worker
from ..core.models import AnalyticsEngine
from ..core.cache import DataStore

class SyncWorker(QObject):
    finished = Signal()
    indices_ready = Signal(str, object)
    gl_ready = Signal(str, list)
    stocks_ready = Signal(object)
    error = Signal(str)
    
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.is_running = True

    @Slot()
    def run_sync(self):
        logger.info("SyncWorker started")
        tasks = [
            ('aspi', self.client.get_aspi_data),
            ('snp', self.client.get_snp_data),
            ('gainers', self.client.get_top_gainers),
            ('losers', self.client.get_top_losers),
            ('stocks', self.client.get_trade_summary)
        ]
        
        for label, fn in tasks:
            if not self.is_running: break
            try:
                logger.info(f"SyncWorker fetching: {label}")
                data = fn()
                if data is None:
                    logger.warning(f"SyncWorker: No data for {label}")
                
                if label in ['aspi', 'snp']:
                    self.indices_ready.emit(label, data)
                elif label in ['gainers', 'losers']:
                    self.gl_ready.emit(label, data or [])
                elif label == 'stocks':
                    self.stocks_ready.emit(data)
                
                # Stagger to avoid overwhelming macOS
                QThread.msleep(500)
            except Exception as e:
                logger.error(f"SyncWorker Error ({label}): {str(e)}")
                self.error.emit(f"{label}: {str(e)}")
        
        logger.info("SyncWorker finished all tasks")
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSE Trade Data Analysis")
        self.client = CSEClient()
        self.db = DataStore()
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(4)
        
        # Setup sync thread
        self.sync_thread = QThread()
        self.sync_worker = SyncWorker(self.client)
        self.sync_worker.moveToThread(self.sync_thread)
        self.sync_thread.started.connect(self.sync_worker.run_sync)
        self.sync_worker.finished.connect(self.sync_thread.quit)
        
        # Connect signals
        self.sync_worker.indices_ready.connect(self.on_index_loaded)
        self.sync_worker.gl_ready.connect(self.on_gl_loaded)
        self.sync_worker.stocks_ready.connect(self.on_stocks_loaded)
        self.sync_worker.error.connect(lambda e: self.status_bar.showMessage(f"Sync Error: {e}", 5000))
        
        self.init_ui()
        self.style_app()
        self.load_cached_data()
        self.load_initial_data()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Main Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel (Dashboard & Screener)
        left_panel = QTabWidget()
        self.dashboard = DashboardWidget()
        self.screener = StockScreenerWidget()
        left_panel.addTab(self.dashboard, "Dashboard")
        left_panel.addTab(self.screener, "Screener")
        
        # Right Panel (Charts)
        self.charts = ChartWidget()
        
        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(self.charts)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(self.splitter)

        # Connect Signals
        self.screener.table.clicked.connect(self.on_stock_selected)
        self.charts.timeframe_selector.currentTextChanged.connect(self.on_timeframe_changed)
        self.screener.export_btn.clicked.connect(self.export_to_csv)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(15)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)

    def style_app(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #121212;
            }
            QTabBar::tab {
                background-color: #1e1e1e;
                color: #b0b0b0;
                padding: 10px 20px;
                border: 1px solid #333;
            }
            QTabBar::tab:selected {
                background-color: #00e676;
                color: black;
                font-weight: bold;
            }
            QSplitter::handle {
                background-color: #333;
            }
        """)

    def load_cached_data(self):
        # Load indices
        aspi = self.db.get_kv('aspi')
        snp = self.db.get_kv('snp')
        if aspi and snp:
            self._last_aspi = aspi
            self._last_snp = snp
            self.dashboard.update_indices(aspi, snp)
            
        # Load G/L
        g = self.db.get_kv('gainers')
        l = self.db.get_kv('losers')
        if g or l:
            self._last_gainers = g or []
            self._last_losers = l or []
            self.dashboard.update_gainers_losers(self._last_gainers, self._last_losers)
            
        # Load Stocks
        stocks = self.db.get_all_stocks()
        if stocks:
            self.on_stocks_loaded(stocks, save_to_cache=False)

    def load_initial_data(self):
        logger.info("Starting initial sync thread")
        self.sync_thread.start()

    def on_index_loaded(self, index_type, data):
        if not data: return
        self.db.set_kv(index_type, data)
        if index_type == 'aspi': self._last_aspi = data
        else: self._last_snp = data
        
        if hasattr(self, '_last_aspi') and hasattr(self, '_last_snp'):
            self.dashboard.update_indices(self._last_aspi, self._last_snp)

    def on_gl_loaded(self, gl_type, data):
        data = data if data else []
        self.db.set_kv(gl_type, data)
        if gl_type == 'gainers': self._last_gainers = data
        else: self._last_losers = data
        
        g = getattr(self, '_last_gainers', [])
        l = getattr(self, '_last_losers', [])
        self.dashboard.update_gainers_losers(g, l)


    def on_stocks_loaded(self, data, save_to_cache=True):
        if not data: return
        
        # Extract stock list
        stock_list = []
        if isinstance(data, dict) and 'reqTradeSummery' in data:
            stock_list = data['reqTradeSummery']
        elif isinstance(data, list):
            stock_list = data
            
        if not stock_list: return

        if save_to_cache:
            self.db.save_stock_summaries(stock_list)
            
        self.screener.update_table(stock_list)
        # Store symbol to securityId mapping (using 'id' from tradeSummary)
        self.symbol_to_id = {s.get('symbol'): s.get('id') for s in stock_list if s.get('symbol')}

    def on_stock_selected(self, index):
        # proxy model index
        row = index.row()
        symbol = self.screener.proxy_model.index(row, 0).data()
        self.selected_symbol = symbol
        self.charts.symbol_label.setText(f"Analyzing: {symbol}")
        
        if hasattr(self, 'symbol_to_id') and symbol in self.symbol_to_id:
            stock_id = self.symbol_to_id.get(symbol)
            if stock_id:
                self.fetch_chart_data(stock_id)
        else:
            self.status_bar.showMessage(f"Error: Could not find ID for {symbol}", 5000)

    def on_timeframe_changed(self, timeframe):
        if hasattr(self, 'selected_symbol') and hasattr(self, 'symbol_to_id'):
            stock_id = self.symbol_to_id.get(self.selected_symbol)
            if stock_id:
                self.fetch_chart_data(stock_id)

    def fetch_chart_data(self, stock_id, period="1"):
        self.progress_bar.show()
        
        # Define a processing function to run in the worker
        def get_and_process_data(stock_id, period):
            raw_data = self.client.get_company_chart_data(stock_id, period=period)
            processed_df = AnalyticsEngine.process_chart_data(raw_data)
            return processed_df

        worker = Worker(get_and_process_data, stock_id, period=period)
        worker.signals.result.connect(self.on_chart_data_loaded)
        worker.signals.finished.connect(lambda: self.progress_bar.hide())
        self.threadpool.start(worker)

    def on_chart_data_loaded(self, df):
        print(f"DEBUG: Chart data loaded: {len(df) if df is not None else 'None'} rows")
        if df is not None and not df.empty:
            self.charts.update_chart(df)
        elif df is None:
            print("DEBUG: Chart dataframe is None")
        else:
            print("DEBUG: Chart dataframe is empty")

    def export_to_csv(self):
        # Simple export of screener data
        import csv
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                headers = [self.screener.model.horizontalHeaderItem(i).text() for i in range(self.screener.model.columnCount())]
                writer.writerow(headers)
                for r in range(self.screener.proxy_model.rowCount()):
                    row_data = [self.screener.proxy_model.index(r, c).data() for c in range(self.screener.proxy_model.columnCount())]
                    writer.writerow(row_data)
            self.status_bar.showMessage(f"Exported to {path}", 3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
