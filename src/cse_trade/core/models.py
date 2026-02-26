import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class MarketIndex:
    name: str
    value: float
    change: float
    percentage_change: float

@dataclass
class StockSummary:
    symbol: str
    name: str
    price: float
    change: float
    percentage_change: float
    volume: int
    turnover: float

class AnalyticsEngine:
    @staticmethod
    def calculate_sma(data: pd.Series, period: int = 20) -> pd.Series:
        return data.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(data: pd.Series, period: int = 20) -> pd.Series:
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_volatility(data: pd.Series, period: int = 20) -> float:
        return data.pct_change().std() * np.sqrt(252) # Annualized volatility

    @staticmethod
    def process_chart_data(api_response) -> pd.DataFrame:
        """
        Processes CSE chart data into a pandas DataFrame.
        Ensures strict numeric types to prevent native crashes in pyqtgraph.
        """
        if api_response is None:
            return pd.DataFrame()
        
        # If response is already a list (as seen in debug)
        if isinstance(api_response, list):
            data = api_response
        elif isinstance(api_response, dict):
            # Check common keys: 'chartData' is common for companyChartDataByStock
            data = api_response.get('chartData', api_response.get('reqChartData', api_response.get('data', [])))
        else:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        if df.empty:
            return df
            
        # Standardize price column
        # 'p' is the price key in companyChartDataByStock
        possible_price_cols = ['p', 'price', 'lastTradedPrice', 'value', 'indexValue']
        found_price = False
        for col in possible_price_cols:
            if col in df.columns:
                # Convert to numeric, coercive errors to NaN
                df['y_price'] = pd.to_numeric(df[col], errors='coerce').astype('float64')
                found_price = True
                break
        
        if not found_price:
            # Last ditch attempt with numeric column
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df['y_price'] = df[numeric_cols[0]].astype('float64')
            else:
                return pd.DataFrame()

        # Handle NaNs in price - fill with forward fill then backward fill if needed
        # This prevents pyqtgraph crashes when encountering NaN in certain modes
        df['y_price'] = df['y_price'].ffill().bfill().fillna(0.0)

        # Standardize timestamp column
        # 't' is the timestamp key in companyChartDataByStock
        timestamp_cols = ['t', 'tradeDate', 'timestamp']
        for col in timestamp_cols:
            if col in df.columns:
                try:
                    df['tradeDate_std'] = pd.to_datetime(df[col], unit='ms')
                except:
                    df['tradeDate_std'] = pd.to_datetime(df[col])
                break
                
        return df
