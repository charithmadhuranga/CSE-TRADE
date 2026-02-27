import sqlite3
import json
import logging
from datetime import datetime

class DataStore:
    def __init__(self, db_path="cse_trade_cache.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Table for key-value pairs (market indices, gainers, losers)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kv_store (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP
                )
            """)
            # Table for stock summaries (screener data)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_summaries (
                    symbol TEXT PRIMARY KEY,
                    data TEXT,
                    updated_at TIMESTAMP
                )
            """)
            # Table for chat history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP
                )
            """)
            conn.commit()

    def set_kv(self, key, value):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO kv_store (key, value, updated_at) VALUES (?, ?, ?)",
                (key, json.dumps(value), datetime.now().isoformat())
            )
            conn.commit()

    def get_kv(self, key):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
                row = cursor.fetchone()
                return json.loads(row[0]) if row else None
        except:
            return None

    def save_chat_history(self, messages):
        """Save chat messages to the database."""
        if not messages:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # We clear and re-save the whole history for simplicity in this version,
            # or we could just append new ones. Let's do a simple append-only logic
            # but we need to know what's already there to avoid duplicates.
            # For simplicity, let's just clear and re-save the whole session history.
            cursor.execute("DELETE FROM chat_history")
            
            for msg in messages:
                from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
                
                role = "unknown"
                if isinstance(msg, HumanMessage):
                    role = "user"
                elif isinstance(msg, AIMessage):
                    role = "assistant"
                elif isinstance(msg, SystemMessage):
                    role = "system"
                
                content = msg.content if hasattr(msg, 'content') else str(msg)
                
                cursor.execute(
                    "INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)",
                    (role, content, datetime.now().isoformat())
                )
            conn.commit()

    def get_chat_history(self):
        """Retrieve chat messages from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT role, content FROM chat_history ORDER BY id ASC")
                rows = cursor.fetchall()
                
                from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
                
                messages = []
                for role, content in rows:
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        messages.append(AIMessage(content=content))
                    elif role == "system":
                        messages.append(SystemMessage(content=content))
                return messages
        except Exception as e:
            logging.error(f"Error loading chat history: {e}")
            return []

    def clear_chat_history(self):
        """Delete all messages from chat history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history")
            conn.commit()

    def save_stock_summaries(self, stock_list):
        if not stock_list: return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            updated_at = datetime.now().isoformat()
            for stock in stock_list:
                symbol = stock.get('symbol')
                if symbol:
                    cursor.execute(
                        "INSERT OR REPLACE INTO stock_summaries (symbol, data, updated_at) VALUES (?, ?, ?)",
                        (symbol, json.dumps(stock), updated_at)
                    )
            conn.commit()

    def get_all_stocks(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM stock_summaries")
                rows = cursor.fetchall()
                return [json.loads(r[0]) for r in rows]
        except:
            return []
