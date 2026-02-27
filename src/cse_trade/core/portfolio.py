import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


class PortfolioManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.expanduser("~/.cse_trade_portfolio.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                company_name TEXT,
                quantity INTEGER NOT NULL,
                avg_price REAL NOT NULL,
                purchase_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total REAL NOT NULL,
                transaction_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                company_name TEXT,
                target_price REAL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_holding(
        self,
        symbol: str,
        quantity: int,
        avg_price: float,
        company_name: str = None,
        purchase_date: str = None,
        notes: str = None,
    ):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO holdings (symbol, company_name, quantity, avg_price, purchase_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (symbol.upper(), company_name, quantity, avg_price, purchase_date, notes),
        )

        conn.commit()
        conn.close()

    def update_holding(
        self, holding_id: int, quantity: int = None, avg_price: float = None
    ):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if quantity is not None:
            cursor.execute(
                "UPDATE holdings SET quantity = ? WHERE id = ?", (quantity, holding_id)
            )
        if avg_price is not None:
            cursor.execute(
                "UPDATE holdings SET avg_price = ? WHERE id = ?",
                (avg_price, holding_id),
            )

        conn.commit()
        conn.close()

    def remove_holding(self, holding_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM holdings WHERE id = ?", (holding_id,))
        conn.commit()
        conn.close()

    def clear_all_holdings(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM holdings")
        conn.commit()
        conn.close()

    def get_holdings(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM holdings ORDER BY symbol")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_transaction(
        self,
        symbol: str,
        transaction_type: str,
        quantity: int,
        price: float,
        total: float,
        transaction_date: str = None,
        notes: str = None,
    ):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO transactions (symbol, transaction_type, quantity, price, total, transaction_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                symbol.upper(),
                transaction_type,
                quantity,
                price,
                total,
                transaction_date,
                notes,
            ),
        )

        conn.commit()
        conn.close()

    def get_transactions(self, symbol: str = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if symbol:
            cursor.execute(
                "SELECT * FROM transactions WHERE symbol = ? ORDER BY transaction_date DESC",
                (symbol.upper(),),
            )
        else:
            cursor.execute("SELECT * FROM transactions ORDER BY transaction_date DESC")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def clear_all_transactions(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions")
        conn.commit()
        conn.close()

    def add_to_watchlist(
        self,
        symbol: str,
        company_name: str = None,
        target_price: float = None,
        notes: str = None,
    ):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO watchlist (symbol, company_name, target_price, notes)
            VALUES (?, ?, ?, ?)
        """,
            (symbol.upper(), company_name, target_price, notes),
        )

        conn.commit()
        conn.close()

    def remove_from_watchlist(self, symbol: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol.upper(),))
        conn.commit()
        conn.close()

    def clear_all_watchlist(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM watchlist")
        conn.commit()
        conn.close()

    def get_watchlist(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM watchlist ORDER BY symbol")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def is_in_watchlist(self, symbol: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM watchlist WHERE symbol = ?", (symbol.upper(),))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def update_watchlist_target(self, symbol: str, target_price: float):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE watchlist SET target_price = ? WHERE symbol = ?",
            (target_price, symbol.upper()),
        )
        conn.commit()
        conn.close()

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        holdings = self.get_holdings()

        total_invested = 0
        total_current = 0
        holdings_data = []

        for h in holdings:
            symbol = h["symbol"]
            quantity = h["quantity"]
            avg_price = h["avg_price"]
            current_price = current_prices.get(symbol, avg_price)

            invested = quantity * avg_price
            current_value = quantity * current_price
            pnl = current_value - invested
            pnl_pct = (pnl / invested * 100) if invested > 0 else 0

            total_invested += invested
            total_current += current_value

            holdings_data.append(
                {
                    **h,
                    "current_price": current_price,
                    "current_value": current_value,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                }
            )

        total_pnl = total_current - total_invested
        total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0

        return {
            "holdings": holdings_data,
            "total_invested": total_invested,
            "total_current": total_current,
            "total_pnl": total_pnl,
            "total_pnl_pct": total_pnl_pct,
        }
