import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans


class StatisticsEngine:
    @staticmethod
    def calculate_market_breadth(stocks: List[Dict]) -> Dict[str, int]:
        """Calculate advances, declines, and unchanged from stock data"""
        advances = 0
        declines = 0
        unchanged = 0

        for stock in stocks:
            change = stock.get("change", stock.get("percentageChange", 0))
            try:
                change = float(change)
                if change > 0:
                    advances += 1
                elif change < 0:
                    declines += 1
                else:
                    unchanged += 1
            except (ValueError, TypeError):
                unchanged += 1

        return {
            "advances": advances,
            "declines": declines,
            "unchanged": unchanged,
            "total": advances + declines + unchanged,
        }

    @staticmethod
    def calculate_market_cap_distribution(stocks: List[Dict]) -> Dict[str, Any]:
        """Calculate market cap distribution statistics"""
        market_caps = []
        for stock in stocks:
            mc = stock.get("marketCap")
            if mc and mc > 0:
                market_caps.append(mc)

        if not market_caps:
            return {}

        market_caps = np.array(market_caps)

        return {
            "mean_market_cap": np.mean(market_caps),
            "median_market_cap": np.median(market_caps),
            "total_market_cap": np.sum(market_caps),
            "top10_market_cap_percent": np.sum(np.sort(market_caps)[-10:])
            / np.sum(market_caps)
            * 100
            if len(market_caps) >= 10
            else 0,
        }

    @staticmethod
    def calculate_volume_statistics(stocks: List[Dict]) -> Dict[str, float]:
        """Calculate volume distribution statistics"""
        volumes = []
        for stock in stocks:
            vol = stock.get("tradevolume", stock.get("sharevolume", 0))
            if vol and vol > 0:
                volumes.append(vol)

        if not volumes:
            return {}

        volumes = np.array(volumes)

        return {
            "total_volume": np.sum(volumes),
            "avg_volume": np.mean(volumes),
            "median_volume": np.median(volumes),
            "volume_std": np.std(volumes),
            "top5_volume_symbols": [],
        }

    @staticmethod
    def calculate_price_statistics(stocks: List[Dict]) -> Dict[str, Any]:
        """Calculate price distribution statistics"""
        prices = []
        for stock in stocks:
            price = stock.get("price", 0)
            if price and price > 0:
                prices.append(price)

        if not prices:
            return {}

        prices = np.array(prices)

        return {
            "mean_price": np.mean(prices),
            "median_price": np.median(prices),
            "min_price": np.min(prices),
            "max_price": np.max(prices),
            "price_std": np.std(prices),
            "price_skewness": stats.skew(prices),
            "price_kurtosis": stats.kurtosis(prices),
        }

    @staticmethod
    def calculate_performance_metrics(stocks: List[Dict]) -> Dict[str, Any]:
        """Calculate overall market performance metrics"""
        changes = []
        for stock in stocks:
            chg = stock.get("percentageChange", stock.get("changePercentage", 0))
            try:
                changes.append(float(chg))
            except (ValueError, TypeError):
                changes.append(0)

        if not changes:
            return {}

        changes = np.array(changes)

        return {
            "mean_change": np.mean(changes),
            "median_change": np.median(changes),
            "change_std": np.std(changes),
            "positive_count": np.sum(changes > 0),
            "negative_count": np.sum(changes < 0),
            "flat_count": np.sum(changes == 0),
            "market_sentiment": "BULLISH"
            if np.mean(changes) > 0
            else "BEARISH"
            if np.mean(changes) < 0
            else "NEUTRAL",
        }

    @staticmethod
    def calculate_percentile_ranks(stocks: List[Dict]) -> List[Dict]:
        """Calculate percentile ranks for each stock"""
        if not stocks:
            return []

        prices = [s.get("price", 0) for s in stocks if s.get("price", 0) > 0]
        volumes = [s.get("tradevolume", s.get("sharevolume", 0)) for s in stocks]
        changes = [
            s.get("percentageChange", s.get("changePercentage", 0)) for s in stocks
        ]

        if prices:
            price_percentiles = (
                stats.rankdata(prices, method="average") / len(prices) * 100
            )
        else:
            price_percentiles = []

        if volumes:
            volume_percentiles = (
                stats.rankdata(volumes, method="average") / len(volumes) * 100
            )
        else:
            volume_percentiles = []

        result = []
        idx_p = 0
        idx_v = 0

        for stock in stocks:
            symbol = stock.get("symbol", "N/A")
            if ".N" in symbol:
                symbol = symbol.split(".N")[0]

            price_pct = (
                price_percentiles[idx_p] if idx_p < len(price_percentiles) else 0
            )
            vol_pct = (
                volume_percentiles[idx_v] if idx_v < len(volume_percentiles) else 0
            )

            result.append(
                {
                    "symbol": symbol,
                    "price_percentile": price_pct,
                    "volume_percentile": vol_pct,
                    "composite_score": (price_pct + vol_pct) / 2,
                }
            )

            if stock.get("price", 0) > 0:
                idx_p += 1
            if stock.get("tradevolume", stock.get("sharevolume", 0)) > 0:
                idx_v += 1

        return sorted(result, key=lambda x: x["composite_score"], reverse=True)

    @staticmethod
    def cluster_stocks(stocks: List[Dict], n_clusters: int = 5) -> Dict[int, List[str]]:
        """Cluster stocks based on price, volume, and change"""
        if len(stocks) < n_clusters:
            return {}

        features = []
        for stock in stocks:
            price = stock.get("price", 0) or 0
            volume = stock.get("tradevolume", stock.get("sharevolume", 0)) or 0
            change = (
                stock.get("percentageChange", stock.get("changePercentage", 0)) or 0
            )

            if price > 0 and volume > 0:
                features.append([price, volume, change])

        if len(features) < n_clusters:
            return {}

        features = np.array(features)

        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        # K-Means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features_scaled)

        clusters = {}
        idx = 0
        for stock in stocks:
            if (
                stock.get("price", 0) > 0
                and stock.get("tradevolume", stock.get("sharevolume", 0)) > 0
            ):
                cluster_id = int(labels[idx])
                symbol = stock.get("symbol", "N/A")
                if ".N" in symbol:
                    symbol = symbol.split(".N")[0]

                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(symbol)
                idx += 1

        return clusters

    @staticmethod
    def calculate_momentum_indicators(stocks: List[Dict]) -> Dict[str, Any]:
        """Calculate momentum-based market indicators"""
        changes = []
        for stock in stocks:
            chg = stock.get("percentageChange", stock.get("changePercentage", 0))
            try:
                changes.append(float(chg))
            except (ValueError, TypeError):
                changes.append(0)

        if not changes:
            return {}

        changes = np.array(changes)

        # Calculate various momentum indicators
        positive_ratio = np.sum(changes > 0) / len(changes)

        # Momentum score (weighted by magnitude)
        momentum_score = np.sum(np.sign(changes) * np.abs(changes)) / len(changes)

        # Strength indicator
        if np.std(changes) > 0:
            t_stat = np.mean(changes) / (np.std(changes) / np.sqrt(len(changes)))
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), len(changes) - 1))
        else:
            t_stat = 0
            p_value = 1

        return {
            "positive_ratio": positive_ratio,
            "momentum_score": momentum_score,
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant": p_value < 0.05,
            "momentum_direction": "UP"
            if momentum_score > 0.5
            else "DOWN"
            if momentum_score < -0.5
            else "SIDEWAYS",
        }

    @staticmethod
    def calculate_volatility_metrics(stocks: List[Dict]) -> Dict[str, float]:
        """Calculate market volatility metrics"""
        changes = []
        for stock in stocks:
            chg = stock.get("percentageChange", stock.get("changePercentage", 0))
            try:
                changes.append(float(chg))
            except (ValueError, TypeError):
                changes.append(0)

        if not changes:
            return {}

        changes = np.array(changes)

        # Historical volatility (annualized)
        # Note: changes are already in percentage form (e.g., 1.5 = 1.5%)
        # So we don't multiply by 100 again
        daily_vol = np.std(changes)
        volatility = daily_vol * np.sqrt(252)

        # Calculate Value at Risk (VaR) at 95% confidence
        var_95 = np.percentile(changes, 5)

        # Calculate Conditional VaR (Expected Shortfall)
        cvar_95 = (
            np.mean(changes[changes <= var_95]) if np.any(changes <= var_95) else var_95
        )

        return {
            "volatility_percent": volatility,
            "var_95": var_95,
            "cvar_95": cvar_95,
            "daily_volatility": np.std(changes),
            "price_range": np.max(changes) - np.min(changes),
        }

    @staticmethod
    def get_all_statistics(stocks: List[Dict]) -> Dict[str, Any]:
        """Get comprehensive market statistics"""
        return {
            "market_breadth": StatisticsEngine.calculate_market_breadth(stocks),
            "market_cap": StatisticsEngine.calculate_market_cap_distribution(stocks),
            "volume": StatisticsEngine.calculate_volume_statistics(stocks),
            "price": StatisticsEngine.calculate_price_statistics(stocks),
            "performance": StatisticsEngine.calculate_performance_metrics(stocks),
            "momentum": StatisticsEngine.calculate_momentum_indicators(stocks),
            "volatility": StatisticsEngine.calculate_volatility_metrics(stocks),
            "top_percentiles": StatisticsEngine.calculate_percentile_ranks(stocks)[:10],
        }
