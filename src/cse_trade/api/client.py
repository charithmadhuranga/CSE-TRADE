import requests
import json
import logging
import threading

class CSEClient:
    BASE_URL = "https://www.cse.lk/api/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False # Disable netrc lookup to prevent crashes on macOS
        self._lock = threading.Lock()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.cse.lk/",
            "Origin": "https://www.cse.lk",
            "Connection": "keep-alive"
        }
        self.session.headers.update(self.headers)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _post(self, endpoint, payload=None):
        url = f"{self.BASE_URL}{endpoint}"
        try:
            # Thread-safe POST request
            with self._lock:
                response = self.session.post(url, json=payload or {}, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API Error at {endpoint}: {e}")
            return None

    def _post_form(self, endpoint, payload=None):
        url = f"{self.BASE_URL}{endpoint}"
        try:
            # Thread-safe POST Form request
            with self._lock:
                response = self.session.post(url, data=payload or {}, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Form API Error at {endpoint}: {e}")
            return None

    def get_market_summary(self):
        return self._post("marketSummery")

    def get_aspi_data(self):
        return self._post("aspiData")

    def get_snp_data(self):
        return self._post("snpData")

    def get_trade_summary(self):
        return self._post("tradeSummary")

    def get_top_gainers(self):
        return self._post("topGainers")

    def get_top_losers(self):
        return self._post("topLooses")

    def get_chart_data(self, symbol, chart_id="1", period="1Y"):
        """
        Payload example: {"symbol": "SYMBOL", "chartId": "id", "period": "period"}
        """
        payload = {
            "symbol": symbol,
            "chartId": chart_id,
            "period": period
        }
        return self._post_form("chartData", payload)

    def get_company_info(self, symbol):
        """
        Payload: {"symbol": "SYMBOL"}
        """
        payload = {"symbol": symbol}
        return self._post_form("companyInfoSummery", payload)

    def get_company_chart_data(self, stock_id, period="1"):
        """
        Payload: {"stockId": stock_id, "period": "period"}
        """
        payload = {"stockId": stock_id, "period": period}
        return self._post_form("companyChartDataByStock", payload)
