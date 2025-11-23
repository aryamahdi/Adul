# sectors_api.py - Sectors.app API Integration for IDX Stocks
import os
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class SectorsAPI:
    """
    Sectors.app API Integration
    
    Comprehensive Indonesia Stock Exchange (IDX) data provider
    Official API: https://sectors.app/api
    Documentation: https://docs.sectors.app
    
    Features:
    - Real-time stock prices
    - Company financials
    - Top gainers/losers
    - Stock screening
    - Historical data
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Sectors API
        
        Args:
            api_key: Your Sectors.app API key
                     Get it from: https://sectors.app/api
        """
        self.api_key = api_key or os.getenv('SECTORS_API_KEY')
        self.base_url = "https://api.sectors.app/v1"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            logger.warning("SECTORS_API_KEY not set. Some features will be limited.")
    
    async def get_stock_overview(self, ticker: str) -> Optional[Dict]:
        """
        Get comprehensive stock overview
        
        Args:
            ticker: Stock ticker without .JK (e.g., 'BBCA')
        
        Returns:
            Dict with stock data or None if error
        """
        try:
            url = f"{self.base_url}/company/report/{ticker}/"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"Error getting {ticker}: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error in get_stock_overview for {ticker}: {e}")
            return None
    
    async def get_stock_price(self, ticker: str) -> Optional[Dict]:
        """
        Get current stock price and basic info
        
        Args:
            ticker: Stock ticker without .JK
        
        Returns:
            Dict with price data
        """
        try:
            # Get overview which includes price
            overview = await self.get_stock_overview(ticker)
            
            if not overview:
                return None
            
            price_data = {
                'ticker': ticker,
                'price': overview.get('close', 0),
                'open': overview.get('open', 0),
                'high': overview.get('high', 0),
                'low': overview.get('low', 0),
                'volume': overview.get('volume', 0),
                'market_cap': overview.get('market_cap', 0),
                'change': overview.get('daily_change', 0),
                'change_percent': overview.get('daily_change_percent', 0),
                'pe_ratio': overview.get('pe', 0),
                'pb_ratio': overview.get('pb', 0),
                'sector': overview.get('sector', 'N/A'),
                'subsector': overview.get('sub_sector', 'N/A'),
            }
            
            return price_data
            
        except Exception as e:
            logger.error(f"Error getting price for {ticker}: {e}")
            return None
    
    async def get_top_gainers(self, limit: int = 10, period: str = '1_day') -> List[Dict]:
        """
        Get top gaining stocks
        
        Args:
            limit: Number of stocks (max 10)
            period: '1_day', '1_week', '1_month', 'ytd', '1_year'
        
        Returns:
            List of top gainer stocks
        """
        try:
            url = f"{self.base_url}/companies/top-changes/"
            
            params = {
                'top': limit,
                'classification': 'gainer',
                'period': period
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"Error getting top gainers: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error in get_top_gainers: {e}")
            return []
    
    async def get_top_losers(self, limit: int = 10, period: str = '1_day') -> List[Dict]:
        """Get top losing stocks"""
        try:
            url = f"{self.base_url}/companies/top-changes/"
            
            params = {
                'top': limit,
                'classification': 'loser',
                'period': period
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        return []
                        
        except Exception as e:
            logger.error(f"Error in get_top_losers: {e}")
            return []
    
    async def get_most_active(self, limit: int = 10, period: str = '1_day') -> List[Dict]:
        """
        Get most actively traded stocks by volume
        
        Args:
            limit: Number of stocks
            period: Time period
        
        Returns:
            List of most active stocks
        """
        try:
            url = f"{self.base_url}/most-traded/"
            
            params = {
                'top': limit,
                'period': period
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        return []
                        
        except Exception as e:
            logger.error(f"Error in get_most_active: {e}")
            return []
    
    async def get_idx_composite(self) -> Optional[Dict]:
        """Get IDX Composite (IHSG) data"""
        try:
            url = f"{self.base_url}/index/COMPOSITE/"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting IHSG: {e}")
            return None
    
    async def get_company_financials(self, ticker: str) -> Optional[Dict]:
        """
        Get company financial statements
        
        Args:
            ticker: Stock ticker
        
        Returns:
            Financial data including revenue, profit, etc.
        """
        try:
            url = f"{self.base_url}/company/report/{ticker}/"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        financials = {
                            'ticker': ticker,
                            'revenue': data.get('revenue', 0),
                            'net_income': data.get('net_income', 0),
                            'total_assets': data.get('total_assets', 0),
                            'total_equity': data.get('total_equity', 0),
                            'debt_to_equity': data.get('debt_to_equity', 0),
                            'roe': data.get('roe', 0),
                            'roa': data.get('roa', 0),
                            'npm': data.get('npm', 0),
                            'eps': data.get('eps', 0),
                            'bvps': data.get('bvps', 0),
                        }
                        
                        return financials
                    else:
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting financials for {ticker}: {e}")
            return None
    
    async def screen_stocks(self, 
                          min_price: Optional[float] = None,
                          max_price: Optional[float] = None,
                          min_volume: Optional[float] = None,
                          sector: Optional[str] = None) -> List[str]:
        """
        Screen stocks based on criteria
        
        Args:
            min_price: Minimum stock price
            max_price: Maximum stock price
            min_volume: Minimum trading volume
            sector: Sector filter
        
        Returns:
            List of ticker symbols matching criteria
        """
        try:
            # This is a simplified version
            # In production, you'd want more sophisticated screening
            
            # Get all companies
            url = f"{self.base_url}/companies/"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        companies = await response.json()
                        
                        filtered = []
                        for company in companies:
                            ticker = company.get('symbol')
                            
                            # Apply filters
                            if min_price and company.get('close', 0) < min_price:
                                continue
                            if max_price and company.get('close', 0) > max_price:
                                continue
                            if min_volume and company.get('volume', 0) < min_volume:
                                continue
                            if sector and company.get('sector') != sector:
                                continue
                            
                            filtered.append(ticker)
                        
                        return filtered
                    else:
                        return []
                        
        except Exception as e:
            logger.error(f"Error in screen_stocks: {e}")
            return []
    
    async def get_sectors_list(self) -> List[str]:
        """Get list of all sectors in IDX"""
        try:
            url = f"{self.base_url}/sectors/"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [sector['name'] for sector in data]
                    else:
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting sectors: {e}")
            return []
    
    async def get_top_stocks_by_market_cap(self, limit: int = 50) -> List[str]:
        """
        Get top stocks by market capitalization
        
        Args:
            limit: Number of stocks to return
        
        Returns:
            List of ticker symbols
        """
        try:
            url = f"{self.base_url}/companies/top/"
            
            params = {
                'top': limit,
                'sort_by': 'market_cap'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [company['symbol'] for company in data]
                    else:
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting top stocks: {e}")
            return []
    
    async def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if ticker exists in IDX
        
        Args:
            ticker: Stock ticker to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            data = await self.get_stock_price(ticker)
            return data is not None
            
        except:
            return False
    
    async def get_historical_prices(self, ticker: str, days: int = 90) -> Optional[List[Dict]]:
        """
        Get historical price data
        
        Args:
            ticker: Stock ticker
            days: Number of days of history
        
        Returns:
            List of historical price data
        """
        try:
            url = f"{self.base_url}/company/historical/{ticker}/"
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting historical data for {ticker}: {e}")
            return None


# Portfolio Management (Manual - since no broker has public API)
class ManualPortfolio:
    """
    Manual portfolio management
    
    Since Indonesian brokers don't have public APIs,
    users need to manually input their portfolio
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.holdings = []
        # In production, this should use a database
    
    def add_holding(self, ticker: str, quantity: int, avg_price: float, 
                   purchase_date: Optional[str] = None):
        """Add a stock holding to portfolio"""
        holding = {
            'ticker': ticker,
            'quantity': quantity,
            'avg_price': avg_price,
            'purchase_date': purchase_date or datetime.now().strftime('%Y-%m-%d'),
            'date_added': datetime.now().isoformat()
        }
        self.holdings.append(holding)
        return True
    
    def remove_holding(self, ticker: str):
        """Remove a stock from portfolio"""
        self.holdings = [h for h in self.holdings if h['ticker'] != ticker]
        return True
    
    def update_holding(self, ticker: str, quantity: int, avg_price: float):
        """Update existing holding"""
        for holding in self.holdings:
            if holding['ticker'] == ticker:
                holding['quantity'] = quantity
                holding['avg_price'] = avg_price
                return True
        return False
    
    async def get_portfolio_value(self, sectors_api: SectorsAPI) -> Dict:
        """
        Calculate current portfolio value using live prices
        
        Args:
            sectors_api: SectorsAPI instance for getting current prices
        
        Returns:
            Portfolio summary with P/L
        """
        total_cost = 0
        total_value = 0
        holdings_detail = []
        
        for holding in self.holdings:
            ticker = holding['ticker']
            quantity = holding['quantity']
            avg_price = holding['avg_price']
            
            # Get current price
            price_data = await sectors_api.get_stock_price(ticker)
            
            if price_data:
                current_price = price_data['price']
                
                cost = quantity * avg_price * 100  # lot to shares
                value = quantity * current_price * 100
                pl = value - cost
                pl_pct = (pl / cost) * 100 if cost > 0 else 0
                
                total_cost += cost
                total_value += value
                
                holdings_detail.append({
                    'ticker': ticker,
                    'quantity': quantity,
                    'avg_price': avg_price,
                    'current_price': current_price,
                    'cost': cost,
                    'value': value,
                    'pl': pl,
                    'pl_pct': pl_pct
                })
        
        total_pl = total_value - total_cost
        total_pl_pct = (total_pl / total_cost) * 100 if total_cost > 0 else 0
        
        return {
            'total_cost': total_cost,
            'total_value': total_value,
            'total_pl': total_pl,
            'total_pl_pct': total_pl_pct,
            'holdings': holdings_detail,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_holdings(self) -> List[Dict]:
        """Get all holdings"""
        return self.holdings
    
    def clear_portfolio(self):
        """Clear all holdings"""
        self.holdings = []
        return True
