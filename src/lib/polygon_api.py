"""
Polygon.io API client for market data.
Supports tiered access with feature gating based on subscription level.
"""

import requests
from typing import Optional
from datetime import datetime, timedelta
from .database import get_database


# Features available per tier
TIER_FEATURES = {
    'free': ['endOfDayPrices', 'tickerSearch'],
    'starter': ['endOfDayPrices', 'tickerSearch', 'delayedQuotes', 'optionsChain', 'greeks', 'iv'],
    'advanced': ['endOfDayPrices', 'tickerSearch', 'realtimeQuotes', 'optionsChain', 'greeks', 'iv'],
    'business': ['endOfDayPrices', 'tickerSearch', 'realtimeQuotes', 'optionsChain', 'greeks', 'iv', 'historicalOptions']
}


class PolygonAPI:
    """Polygon.io API client with tier-aware feature gating."""
    
    BASE_URL = "https://api.polygon.io"
    
    def __init__(self, api_key: str = "", tier: str = "free"):
        self.api_key = api_key
        self.tier = tier
        self._cache = {}
        self._cache_expiry = {}
    
    @property
    def available_features(self) -> list[str]:
        """Get features available for current tier."""
        return TIER_FEATURES.get(self.tier, TIER_FEATURES['free'])
    
    def has_feature(self, feature: str) -> bool:
        """Check if a feature is available."""
        return feature in self.available_features
    
    def _make_request(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """Make an API request."""
        if not self.api_key:
            return None
        
        if params is None:
            params = {}
        params['apiKey'] = self.api_key
        
        try:
            response = requests.get(f"{self.BASE_URL}{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Polygon API error: {e}")
            return None
    
    def _get_cached(self, cache_key: str, ttl_seconds: int = 300):
        """Get cached value if not expired."""
        if cache_key in self._cache:
            if datetime.now() < self._cache_expiry.get(cache_key, datetime.min):
                return self._cache[cache_key]
        return None
    
    def _set_cached(self, cache_key: str, value, ttl_seconds: int = 300):
        """Set cached value with expiry."""
        self._cache[cache_key] = value
        self._cache_expiry[cache_key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def test_connection(self) -> tuple[bool, str]:
        """Test API connection and return status."""
        if not self.api_key:
            return False, "No API key configured"
        
        result = self._make_request("/v3/reference/tickers", {"limit": 1})
        if result and result.get('status') == 'OK':
            return True, "Connected successfully"
        elif result and 'error' in result:
            return False, result.get('error', 'Unknown error')
        return False, "Connection failed"
    
    # ==================== STOCK DATA ====================
    
    def get_ticker_details(self, ticker: str) -> Optional[dict]:
        """Get ticker details (company info)."""
        cache_key = f"ticker_details_{ticker}"
        cached = self._get_cached(cache_key, 86400)  # Cache for 24 hours
        if cached:
            return cached
        
        result = self._make_request(f"/v3/reference/tickers/{ticker.upper()}")
        if result and result.get('status') == 'OK':
            data = result.get('results', {})
            self._set_cached(cache_key, data, 86400)
            return data
        return None
    
    def search_tickers(self, query: str, limit: int = 10) -> list[dict]:
        """Search for tickers."""
        if not self.has_feature('tickerSearch'):
            return []
        
        result = self._make_request("/v3/reference/tickers", {
            "search": query,
            "active": "true",
            "limit": limit,
            "market": "stocks"
        })
        
        if result and result.get('status') == 'OK':
            return result.get('results', [])
        return []
    
    def get_previous_close(self, ticker: str) -> Optional[dict]:
        """Get previous day close data (free tier)."""
        if not self.has_feature('endOfDayPrices'):
            return None
        
        cache_key = f"prev_close_{ticker}"
        cached = self._get_cached(cache_key, 3600)  # Cache for 1 hour
        if cached:
            return cached
        
        result = self._make_request(f"/v2/aggs/ticker/{ticker.upper()}/prev")
        if result and result.get('status') == 'OK':
            results = result.get('results', [])
            if results:
                data = {
                    'ticker': ticker.upper(),
                    'close': results[0].get('c'),
                    'open': results[0].get('o'),
                    'high': results[0].get('h'),
                    'low': results[0].get('l'),
                    'volume': results[0].get('v'),
                    'vwap': results[0].get('vw'),
                    'timestamp': results[0].get('t')
                }
                self._set_cached(cache_key, data, 3600)
                return data
        return None
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current/latest price for a ticker."""
        # Try real-time quote first if available
        if self.has_feature('realtimeQuotes'):
            result = self._make_request(f"/v2/last/trade/{ticker.upper()}")
            if result and result.get('status') == 'OK':
                return result.get('results', {}).get('p')
        
        # Fall back to previous close
        prev = self.get_previous_close(ticker)
        if prev:
            return prev.get('close')
        
        return None
    
    def get_aggregate_bars(self, ticker: str, timespan: str = "day", 
                          from_date: str = None, to_date: str = None,
                          limit: int = 120) -> list[dict]:
        """Get aggregate bars (OHLCV data)."""
        if not self.has_feature('endOfDayPrices'):
            return []
        
        if to_date is None:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if from_date is None:
            from_date = (datetime.now() - timedelta(days=limit)).strftime("%Y-%m-%d")
        
        result = self._make_request(
            f"/v2/aggs/ticker/{ticker.upper()}/range/1/{timespan}/{from_date}/{to_date}",
            {"limit": limit, "sort": "asc"}
        )
        
        if result and result.get('status') == 'OK':
            return result.get('results', [])
        return []
    
    # ==================== OPTIONS DATA (Paid Tiers) ====================
    
    def get_options_chain(self, ticker: str, expiration_date: str = None,
                         contract_type: str = None) -> list[dict]:
        """Get options chain for a ticker (paid tiers only)."""
        if not self.has_feature('optionsChain'):
            return []
        
        params = {}
        if expiration_date:
            params['expiration_date'] = expiration_date
        if contract_type:
            params['contract_type'] = contract_type
        
        result = self._make_request(
            f"/v3/snapshot/options/{ticker.upper()}",
            params
        )
        
        if result and result.get('status') == 'OK':
            return result.get('results', [])
        return []
    
    def get_option_contract(self, options_ticker: str) -> Optional[dict]:
        """Get details for a specific option contract."""
        if not self.has_feature('optionsChain'):
            return None
        
        result = self._make_request(f"/v3/snapshot/options/{options_ticker}")
        if result and result.get('status') == 'OK':
            results = result.get('results', [])
            if results:
                return results[0]
        return None
    
    # ==================== MARKET INDICES ====================
    
    def get_index_performance(self, days: int = 365) -> dict:
        """Get performance data for major indices."""
        indices = {
            'SPY': 'S&P 500',
            'QQQ': 'Nasdaq',
            'IWM': 'Russell 2000',
            'DIA': 'Dow Jones'
        }
        
        performance = {}
        
        for symbol, name in indices.items():
            bars = self.get_aggregate_bars(symbol, "day", limit=days)
            if bars and len(bars) >= 2:
                start_price = bars[0].get('c', 0)
                end_price = bars[-1].get('c', 0)
                
                if start_price > 0:
                    ytd_return = ((end_price - start_price) / start_price) * 100
                    performance[name] = {
                        'symbol': symbol,
                        'return': round(ytd_return, 2),
                        'current_price': end_price
                    }
        
        return performance


# Global API instance
_api_instance: Optional[PolygonAPI] = None


def get_polygon_api() -> PolygonAPI:
    """Get the global Polygon API instance."""
    global _api_instance
    if _api_instance is None:
        db = get_database()
        api_key = db.get_setting('polygon_api_key') or ""
        tier = db.get_setting('polygon_tier') or "free"
        _api_instance = PolygonAPI(api_key, tier)
    return _api_instance


def refresh_polygon_api():
    """Refresh the Polygon API instance with current settings."""
    global _api_instance
    db = get_database()
    api_key = db.get_setting('polygon_api_key') or ""
    tier = db.get_setting('polygon_tier') or "free"
    _api_instance = PolygonAPI(api_key, tier)
    return _api_instance
