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
        return data.pct_change().std() * np.sqrt(252)

    @staticmethod
    def calculate_macd(
        data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ):
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: int = 2):
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band

    @staticmethod
    def calculate_stochastic(
        high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ):
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        stoch_k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        stoch_d = stoch_k.rolling(window=3).mean()
        return stoch_k, stoch_d

    @staticmethod
    def calculate_momentum(data: pd.Series, period: int = 10) -> pd.Series:
        return data.diff(period)

    @staticmethod
    def calculate_roc(data: pd.Series, period: int = 12) -> pd.Series:
        return ((data - data.shift(period)) / data.shift(period)) * 100

    @staticmethod
    def calculate_atr(
        high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ):
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv

    @staticmethod
    def calculate_cci(
        high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20
    ):
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        cci = (tp - sma_tp) / (0.015 * mad)
        return cci

    @staticmethod
    def calculate_williams_r(
        high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ):
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        return williams_r

    @staticmethod
    def get_all_indicators(df: pd.DataFrame) -> dict:
        if df.empty or "y_price" not in df.columns:
            return {}

        price = df["y_price"]
        indicators = {}

        indicators["sma_20"] = AnalyticsEngine.calculate_sma(price, 20)
        indicators["sma_50"] = AnalyticsEngine.calculate_sma(price, 50)
        indicators["sma_200"] = AnalyticsEngine.calculate_sma(price, 200)
        indicators["ema_20"] = AnalyticsEngine.calculate_ema(price, 20)
        indicators["rsi_14"] = AnalyticsEngine.calculate_rsi(price, 14)

        macd, signal, hist = AnalyticsEngine.calculate_macd(price)
        indicators["macd"] = macd
        indicators["macd_signal"] = signal
        indicators["macd_hist"] = hist

        upper, middle, lower = AnalyticsEngine.calculate_bollinger_bands(price)
        indicators["bb_upper"] = upper
        indicators["bb_middle"] = middle
        indicators["bb_lower"] = lower

        return indicators

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
            data = api_response.get(
                "chartData",
                api_response.get("reqChartData", api_response.get("data", [])),
            )
        else:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        if df.empty:
            return df

        # Standardize price column
        # 'p' is the price key in companyChartDataByStock
        possible_price_cols = ["p", "price", "lastTradedPrice", "value", "indexValue"]
        found_price = False
        for col in possible_price_cols:
            if col in df.columns:
                # Convert to numeric, coercive errors to NaN
                df["y_price"] = pd.to_numeric(df[col], errors="coerce").astype(
                    "float64"
                )
                found_price = True
                break

        if not found_price:
            # Last ditch attempt with numeric column
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df["y_price"] = df[numeric_cols[0]].astype("float64")
            else:
                return pd.DataFrame()

        # Handle NaNs in price - fill with forward fill then backward fill if needed
        # This prevents pyqtgraph crashes when encountering NaN in certain modes
        df["y_price"] = df["y_price"].ffill().bfill().fillna(0.0)

        # Standardize timestamp column
        # 't' is the timestamp key in companyChartDataByStock
        timestamp_cols = ["t", "tradeDate", "timestamp"]
        for col in timestamp_cols:
            if col in df.columns:
                try:
                    df["tradeDate_std"] = pd.to_datetime(df[col], unit="ms")
                except:
                    df["tradeDate_std"] = pd.to_datetime(df[col])
                break

        return df
