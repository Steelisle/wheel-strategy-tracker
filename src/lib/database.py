"""
SQLite database module for Wheel Strategy Tracker.
Handles all database operations for positions, trades, settings, and snapshots.
Supports demo mode with sample data and active mode for real data.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Optional
import random


class Database:
    """Database handler for the Wheel Strategy Tracker."""
    
    def __init__(self, db_path: Optional[str] = None, demo_mode: bool = False):
        self.demo_mode = demo_mode
        
        if db_path is None:
            # Default to data directory
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            
            if demo_mode:
                db_path = str(data_dir / "demo_data.db")
            else:
                db_path = str(data_dir / "wheel_tracker.db")
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        
        # Populate demo data if demo mode and empty
        if demo_mode:
            self._ensure_demo_data()
    
    def _init_schema(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()
        
        # Positions table - tracks stock positions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL UNIQUE,
                shares_owned INTEGER DEFAULT 0,
                cost_basis REAL DEFAULT 0.0,
                current_price REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Trades table - tracks all option trades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id INTEGER,
                type TEXT NOT NULL CHECK(type IN ('CSP', 'CC', 'ASSIGNMENT', 'CLOSE', 'ROLL', 'BUY', 'SELL')),
                ticker TEXT NOT NULL,
                strike REAL,
                expiration DATE,
                premium REAL DEFAULT 0.0,
                quantity INTEGER DEFAULT 1,
                delta REAL,
                status TEXT DEFAULT 'OPEN' CHECK(status IN ('OPEN', 'CLOSED', 'EXPIRED', 'ASSIGNED')),
                notes TEXT,
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                FOREIGN KEY (position_id) REFERENCES positions(id)
            )
        """)
        
        # Settings table - app configuration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Snapshots table - daily portfolio snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date DATE UNIQUE,
                portfolio_value REAL DEFAULT 0.0,
                options_pnl REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Portfolio info table - configurable portfolio details
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_investing TEXT,
                philosophy TEXT,
                options_strategy TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Portfolio milestones table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                date_reached TEXT,
                time_to_reach TEXT,
                sort_order INTEGER DEFAULT 0
            )
        """)
        
        # Initialize default settings
        default_settings = {
            'polygon_api_key': '',
            'polygon_tier': 'free',
            'theme': 'dark'
        }
        
        for key, value in default_settings.items():
            cursor.execute("""
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            """, (key, value))
        
        self.conn.commit()
    
    def _ensure_demo_data(self):
        """Ensure demo database has sample data."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trades")
        count = cursor.fetchone()[0]
        
        if count == 0:
            self._populate_demo_data()
    
    def _populate_demo_data(self):
        """Populate the demo database with sample data for 2026."""
        # Sample tickers with typical wheel strategy stocks (2026 data only)
        tickers = [
            ("FLY", 98, 0),
            ("RDW", 80, 0),
            ("ARM", 45, 0),
            ("ACB", 0, 40),
            ("RKT", 40, 0),
            ("SOFI", 29, 0),
            ("ACHR", 6, 21),
            ("USAR", 25, 0),
            ("WULF", 19, 0),
            ("TOST", 16, 0),
            ("SMMT", 15, 0),
            ("HE", 13, 0),
            ("BBAI", 7, 0),
            ("NIO", 0, 5),
        ]
        
        from datetime import timedelta
        
        # First trade date is Jan 6, 2026 (start of Week 1)
        first_trade_date = datetime(2026, 1, 6)
        
        for i, (ticker, cc_premium, csp_premium) in enumerate(tickers):
            # Create position
            pos = self.get_or_create_position(ticker)
            
            # Add some shares for tickers with covered calls
            if cc_premium > 0:
                self.update_position(pos['id'], shares=100, cost_basis=random.uniform(10, 50))
            
            # Spread trades across the first few weeks of 2026
            trade_date = first_trade_date + timedelta(days=i % 12)
            
            # Add covered call trade if applicable
            if cc_premium > 0:
                exp_date = (trade_date + timedelta(days=random.randint(14, 45))).strftime("%Y-%m-%d")
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO trades (position_id, type, ticker, strike, expiration, premium, quantity, delta, status, opened_at, closed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'EXPIRED', ?, ?)
                """, (
                    pos['id'],
                    'CC',
                    ticker,
                    random.uniform(15, 100),
                    exp_date,
                    cc_premium / 100,
                    1,
                    random.uniform(0.10, 0.25),
                    trade_date.strftime("%Y-%m-%d %H:%M:%S"),
                    trade_date.strftime("%Y-%m-%d %H:%M:%S")
                ))
            
            # Add CSP trade if applicable
            if csp_premium > 0:
                exp_date = (trade_date + timedelta(days=random.randint(14, 45))).strftime("%Y-%m-%d")
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO trades (position_id, type, ticker, strike, expiration, premium, quantity, delta, status, opened_at, closed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'EXPIRED', ?, ?)
                """, (
                    pos['id'],
                    'CSP',
                    ticker,
                    random.uniform(10, 50),
                    exp_date,
                    csp_premium / 100,
                    1,
                    random.uniform(-0.20, -0.10),
                    trade_date.strftime("%Y-%m-%d %H:%M:%S"),
                    trade_date.strftime("%Y-%m-%d %H:%M:%S")
                ))
        
        self.conn.commit()
        
        # Add sample portfolio info for demo
        self.save_portfolio_info(
            started_investing="January 2026",
            philosophy="I'm a long-term buy-and-hold investor first, and I use simple options as a tool to generate income and improve entries, not to speculate.",
            options_strategy="I primarily sell covered calls and cash-secured puts (CSPs) at conservative deltas (.1-.2), aiming to let them expire worthless and keep the premium. I use LEAPS as a long-dated trial for owning shares outright. I rarely close early, prefer rolling when needed, and let time decay do the heavy lifting while I stay focused on quality companies, patience, and consistency over hype."
        )
        
        # Add sample milestones for demo
        self.save_milestones([
            {'amount': 10000, 'date_reached': 'Jan 2026', 'time_to_reach': 'Starting'},
        ])
    
    # ==================== POSITIONS ====================
    
    def get_all_positions(self) -> list[dict]:
        """Get all positions with their premium summaries."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                p.*,
                COALESCE(SUM(CASE WHEN t.type = 'CC' AND t.status != 'OPEN' THEN t.premium * t.quantity * 100 ELSE 0 END), 0) as cc_premium,
                COALESCE(SUM(CASE WHEN t.type = 'CSP' AND t.status != 'OPEN' THEN t.premium * t.quantity * 100 ELSE 0 END), 0) as csp_premium,
                COALESCE(SUM(CASE WHEN t.type IN ('CC', 'CSP') AND t.status != 'OPEN' THEN t.premium * t.quantity * 100 ELSE 0 END), 0) as total_premium
            FROM positions p
            LEFT JOIN trades t ON p.id = t.position_id
            GROUP BY p.id
            ORDER BY total_premium DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_position(self, ticker: str) -> Optional[dict]:
        """Get a single position by ticker."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE ticker = ?", (ticker.upper(),))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def create_position(self, ticker: str, shares: int = 0, cost_basis: float = 0.0) -> int:
        """Create a new position."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO positions (ticker, shares_owned, cost_basis)
            VALUES (?, ?, ?)
        """, (ticker.upper(), shares, cost_basis))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_position(self, position_id: int, shares: int = None, cost_basis: float = None, current_price: float = None):
        """Update a position."""
        updates = []
        values = []
        
        if shares is not None:
            updates.append("shares_owned = ?")
            values.append(shares)
        if cost_basis is not None:
            updates.append("cost_basis = ?")
            values.append(cost_basis)
        if current_price is not None:
            updates.append("current_price = ?")
            values.append(current_price)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(position_id)
            
            cursor = self.conn.cursor()
            cursor.execute(f"""
                UPDATE positions SET {', '.join(updates)} WHERE id = ?
            """, values)
            self.conn.commit()
    
    def get_or_create_position(self, ticker: str) -> dict:
        """Get existing position or create new one."""
        position = self.get_position(ticker)
        if not position:
            position_id = self.create_position(ticker)
            position = {'id': position_id, 'ticker': ticker.upper(), 'shares_owned': 0, 'cost_basis': 0.0}
        return position
    
    # ==================== TRADES ====================
    
    def get_all_trades(self, status: str = None, trade_type: str = None) -> list[dict]:
        """Get all trades with optional filtering."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM trades WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        if trade_type:
            query += " AND type = ?"
            params.append(trade_type)
        
        query += " ORDER BY opened_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_trades_for_position(self, position_id: int) -> list[dict]:
        """Get all trades for a position."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM trades WHERE position_id = ? ORDER BY opened_at DESC
        """, (position_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def create_trade(self, ticker: str, trade_type: str, strike: float = None,
                     expiration: str = None, premium: float = 0.0, quantity: int = 1,
                     delta: float = None, notes: str = None) -> int:
        """Create a new trade."""
        position = self.get_or_create_position(ticker)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO trades (position_id, type, ticker, strike, expiration, premium, quantity, delta, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (position['id'], trade_type, ticker.upper(), strike, expiration, premium, quantity, delta, notes))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_trade(self, trade_id: int, status: str = None, closed_at: str = None):
        """Update trade status."""
        updates = []
        values = []
        
        if status:
            updates.append("status = ?")
            values.append(status)
        if closed_at:
            updates.append("closed_at = ?")
            values.append(closed_at)
        
        if updates:
            values.append(trade_id)
            cursor = self.conn.cursor()
            cursor.execute(f"""
                UPDATE trades SET {', '.join(updates)} WHERE id = ?
            """, values)
            self.conn.commit()
    
    def close_trade(self, trade_id: int, status: str = 'CLOSED'):
        """Close a trade."""
        self.update_trade(trade_id, status=status, closed_at=datetime.now().isoformat())
    
    # ==================== PREMIUM CALCULATIONS ====================
    
    def get_first_trade_date(self) -> Optional[date]:
        """Get the date of the first trade (start of Week 1)."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT MIN(date(opened_at)) as first_date
            FROM trades 
            WHERE type IN ('CC', 'CSP')
        """)
        row = cursor.fetchone()
        if row and row['first_date']:
            return datetime.strptime(row['first_date'], "%Y-%m-%d").date()
        return None
    
    def get_current_week_number(self) -> int:
        """Get the current week number based on first trade date."""
        first_trade = self.get_first_trade_date()
        if not first_trade:
            return 0  # No trades yet
        
        today = date.today()
        days_since_start = (today - first_trade).days
        return (days_since_start // 7) + 1
    
    def get_premium_summary(self) -> dict:
        """Get premium summary for different time periods."""
        cursor = self.conn.cursor()
        today = date.today()
        
        # Get first trade date for week calculation
        first_trade = self.get_first_trade_date()
        week_number = self.get_current_week_number()
        
        # Calculate current week's start date based on first trade
        if first_trade:
            weeks_elapsed = (today - first_trade).days // 7
            current_week_start = first_trade + timedelta(days=weeks_elapsed * 7)
        else:
            current_week_start = today
        
        # This week's premium (based on first trade date)
        cursor.execute("""
            SELECT COALESCE(SUM(premium * quantity * 100), 0) as total
            FROM trades 
            WHERE type IN ('CC', 'CSP') 
            AND status != 'OPEN'
            AND date(opened_at) >= ?
        """, (current_week_start.isoformat(),))
        week_premium = cursor.fetchone()['total']
        
        # This month's premium
        cursor.execute("""
            SELECT COALESCE(SUM(premium * quantity * 100), 0) as total
            FROM trades 
            WHERE type IN ('CC', 'CSP') 
            AND status != 'OPEN'
            AND strftime('%Y-%m', opened_at) = strftime('%Y-%m', 'now')
        """)
        month_premium = cursor.fetchone()['total']
        
        # YTD premium (based on first trade year, not calendar year)
        if first_trade:
            start_year = first_trade.year
        else:
            start_year = today.year
            
        cursor.execute("""
            SELECT COALESCE(SUM(premium * quantity * 100), 0) as total
            FROM trades 
            WHERE type IN ('CC', 'CSP') 
            AND status != 'OPEN'
            AND strftime('%Y', opened_at) = ?
        """, (str(start_year),))
        ytd_premium = cursor.fetchone()['total']
        
        # All years with trades (for historical display)
        yearly_premiums = {}
        cursor.execute("""
            SELECT strftime('%Y', opened_at) as year, 
                   COALESCE(SUM(premium * quantity * 100), 0) as total
            FROM trades 
            WHERE type IN ('CC', 'CSP') 
            AND status != 'OPEN'
            GROUP BY year
            ORDER BY year DESC
        """)
        for row in cursor.fetchall():
            yearly_premiums[row['year']] = row['total']
        
        # Calculate year-end projection based on days since first trade
        if first_trade and first_trade.year == today.year:
            days_elapsed = (today - first_trade).days + 1
            days_remaining_in_year = (date(today.year, 12, 31) - today).days
            total_days = days_elapsed + days_remaining_in_year
            projected = (ytd_premium / days_elapsed) * total_days if days_elapsed > 0 else 0
        else:
            days_elapsed = (today - today.replace(month=1, day=1)).days + 1
            days_in_year = 366 if today.year % 4 == 0 else 365
            projected = (ytd_premium / days_elapsed) * days_in_year if days_elapsed > 0 else 0
        
        return {
            'week': week_premium,
            'week_number': week_number,
            'month': month_premium,
            'ytd': ytd_premium,
            'yearly': yearly_premiums,
            'projected': projected,
            'first_trade_date': first_trade
        }
    
    def get_top_performers(self, period: str = 'mtd', limit: int = 5) -> list[dict]:
        """Get top performing tickers by premium."""
        cursor = self.conn.cursor()
        
        if period == 'mtd':
            date_filter = "strftime('%Y-%m', opened_at) = strftime('%Y-%m', 'now')"
        else:  # ytd
            date_filter = "strftime('%Y', opened_at) = strftime('%Y', 'now')"
        
        cursor.execute(f"""
            SELECT ticker, 
                   COALESCE(SUM(premium * quantity * 100), 0) as total_premium
            FROM trades 
            WHERE type IN ('CC', 'CSP') 
            AND status != 'OPEN'
            AND {date_filter}
            GROUP BY ticker
            ORDER BY total_premium DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== SETTINGS ====================
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else None
    
    def set_setting(self, key: str, value: str):
        """Set a setting value."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        """, (key, value))
        self.conn.commit()
    
    def get_all_settings(self) -> dict:
        """Get all settings as a dictionary."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        return {row['key']: row['value'] for row in cursor.fetchall()}
    
    # ==================== SNAPSHOTS ====================
    
    def save_snapshot(self, portfolio_value: float, options_pnl: float):
        """Save a daily snapshot."""
        cursor = self.conn.cursor()
        today = date.today().isoformat()
        cursor.execute("""
            INSERT OR REPLACE INTO snapshots (snapshot_date, portfolio_value, options_pnl)
            VALUES (?, ?, ?)
        """, (today, portfolio_value, options_pnl))
        self.conn.commit()
    
    def get_snapshots(self, days: int = 365) -> list[dict]:
        """Get snapshots for the last N days."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM snapshots 
            WHERE snapshot_date >= date('now', ?)
            ORDER BY snapshot_date ASC
        """, (f'-{days} days',))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== PORTFOLIO INFO ====================
    
    def get_portfolio_info(self) -> dict:
        """Get portfolio info."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM portfolio_info LIMIT 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {
            'started_investing': '',
            'philosophy': '',
            'options_strategy': ''
        }
    
    def save_portfolio_info(self, started_investing: str, philosophy: str, options_strategy: str):
        """Save or update portfolio info."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM portfolio_info LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            cursor.execute("""
                UPDATE portfolio_info 
                SET started_investing = ?, philosophy = ?, options_strategy = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (started_investing, philosophy, options_strategy, row['id']))
        else:
            cursor.execute("""
                INSERT INTO portfolio_info (started_investing, philosophy, options_strategy)
                VALUES (?, ?, ?)
            """, (started_investing, philosophy, options_strategy))
        self.conn.commit()
    
    def get_milestones(self) -> list[dict]:
        """Get portfolio milestones."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM portfolio_milestones ORDER BY sort_order ASC")
        return [dict(row) for row in cursor.fetchall()]
    
    def save_milestones(self, milestones: list[dict]):
        """Save portfolio milestones (replaces existing)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM portfolio_milestones")
        
        for i, m in enumerate(milestones):
            cursor.execute("""
                INSERT INTO portfolio_milestones (amount, date_reached, time_to_reach, sort_order)
                VALUES (?, ?, ?, ?)
            """, (m.get('amount', 0), m.get('date_reached', ''), m.get('time_to_reach', ''), i))
        self.conn.commit()
    
    def close(self):
        """Close the database connection."""
        self.conn.close()


# Global database instances
_db_instance: Optional[Database] = None
_demo_db_instance: Optional[Database] = None
_current_mode: str = "active"  # "active" or "demo"


def get_database() -> Database:
    """Get the current database instance based on mode."""
    global _db_instance, _demo_db_instance, _current_mode
    
    if _current_mode == "demo":
        if _demo_db_instance is None:
            _demo_db_instance = Database(demo_mode=True)
        return _demo_db_instance
    else:
        if _db_instance is None:
            _db_instance = Database(demo_mode=False)
        return _db_instance


def set_demo_mode(enabled: bool):
    """Switch between demo and active mode."""
    global _current_mode
    _current_mode = "demo" if enabled else "active"
    # Pre-initialize the database for the new mode
    get_database()


def is_demo_mode() -> bool:
    """Check if demo mode is enabled."""
    return _current_mode == "demo"
