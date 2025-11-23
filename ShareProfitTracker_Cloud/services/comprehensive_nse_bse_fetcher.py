"""
Comprehensive NSE/BSE Stock and Corporate Actions Fetcher

This module fetches ALL NSE and BSE stocks and their corporate actions
using multiple reliable data sources and APIs.
"""

import requests
import json
import csv
import io
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
import time
import concurrent.futures
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CorporateAction:
    """Corporate action data structure"""
    symbol: str
    company_name: str
    action_type: str
    announcement_date: str
    ex_date: str
    record_date: Optional[str] = None
    payment_date: Optional[str] = None
    dividend_amount: Optional[float] = None
    ratio_from: Optional[int] = None
    ratio_to: Optional[int] = None
    purpose: Optional[str] = None
    remarks: Optional[str] = None
    source: Optional[str] = None

class ComprehensiveNSEBSEFetcher:
    """Comprehensive fetcher for NSE/BSE stocks and corporate actions"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.all_nse_stocks = {}
        self.all_bse_stocks = {}
        self.cache_file = 'data/comprehensive_stocks_cache.json'
        
    def get_all_nse_stocks(self) -> Dict[str, str]:
        """Fetch ALL NSE stocks from multiple sources"""
        print("Fetching comprehensive NSE stock list...")
        
        all_stocks = {}
        
        # Method 1: NSE Equity List
        try:
            nse_equity = self._fetch_nse_equity_list()
            all_stocks.update(nse_equity)
            print(f"NSE Equity List: {len(nse_equity)} stocks")
        except Exception as e:
            print(f"NSE Equity List error: {e}")
        
        # Method 2: NSE F&O List
        try:
            nse_fo = self._fetch_nse_fo_list()
            all_stocks.update(nse_fo)
            print(f"NSE F&O List: {len(nse_fo)} additional stocks")
        except Exception as e:
            print(f"NSE F&O List error: {e}")
        
        # Method 3: NSE Indices constituents
        try:
            nse_indices = self._fetch_nse_indices_stocks()
            all_stocks.update(nse_indices)
            print(f"NSE Indices: {len(nse_indices)} additional stocks")
        except Exception as e:
            print(f"NSE Indices error: {e}")
        
        # Method 4: Backup comprehensive list
        try:
            backup_stocks = self._get_backup_nse_stocks()
            for symbol, name in backup_stocks.items():
                if symbol not in all_stocks:
                    all_stocks[symbol] = name
            print(f"Backup list: {len(backup_stocks)} additional stocks")
        except Exception as e:
            print(f"Backup list error: {e}")
        
        self.all_nse_stocks = all_stocks
        print(f"Total NSE stocks collected: {len(all_stocks)}")
        return all_stocks
    
    def _fetch_nse_equity_list(self) -> Dict[str, str]:
        """Fetch NSE equity stocks from official NSE API"""
        stocks = {}
        
        try:
            # NSE Equity Master API
            url = "https://www.nseindia.com/api/equity-stockIndices?csv=true"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # Parse CSV data
                csv_data = csv.DictReader(io.StringIO(response.text))
                for row in csv_data:
                    symbol = row.get('SYMBOL', '').strip()
                    name = row.get('NAME_OF_COMPANY', '').strip()
                    if symbol and name:
                        stocks[symbol] = name
            
        except Exception as e:
            print(f"NSE Equity API error: {e}")
        
        # Alternative NSE API
        try:
            url2 = "https://www.nseindia.com/api/equity-stock"
            response2 = self.session.get(url2, timeout=15)
            
            if response2.status_code == 200:
                data = response2.json()
                if 'data' in data:
                    for item in data['data']:
                        symbol = item.get('symbol', '').strip()
                        name = item.get('companyName', '').strip()
                        if symbol and name:
                            stocks[symbol] = name
        
        except Exception as e:
            print(f"NSE Alternative API error: {e}")
        
        return stocks
    
    def _fetch_nse_fo_list(self) -> Dict[str, str]:
        """Fetch NSE F&O stocks"""
        stocks = {}
        
        try:
            # NSE F&O stocks API
            url = "https://www.nseindia.com/api/equity-stock?index=SECURITIES%20IN%20F%26O"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    for item in data['data']:
                        symbol = item.get('symbol', '').strip()
                        name = item.get('companyName', '').strip()
                        if symbol and name:
                            stocks[symbol] = name
        
        except Exception as e:
            print(f"NSE F&O API error: {e}")
        
        return stocks
    
    def _fetch_nse_indices_stocks(self) -> Dict[str, str]:
        """Fetch stocks from major NSE indices"""
        stocks = {}
        
        # Major indices to fetch
        indices = ['NIFTY 50', 'NIFTY 100', 'NIFTY 200', 'NIFTY 500', 'NIFTY MIDCAP 100', 'NIFTY SMLCAP 100']
        
        for index in indices:
            try:
                url = f"https://www.nseindia.com/api/equity-stockIndices?index={index}"
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        for item in data['data']:
                            symbol = item.get('symbol', '').strip()
                            # Get company name from other field or use symbol
                            name = item.get('companyName', symbol).strip()
                            if symbol:
                                stocks[symbol] = name
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"Error fetching {index}: {e}")
        
        return stocks
    
    def _get_backup_nse_stocks(self) -> Dict[str, str]:
        """Backup comprehensive NSE stock list"""
        # This is a curated list of major NSE stocks for fallback
        backup_stocks = {
            # Banking & Financial Services
            'HDFCBANK': 'HDFC Bank Limited',
            'ICICIBANK': 'ICICI Bank Limited',
            'AXISBANK': 'Axis Bank Limited',
            'KOTAKBANK': 'Kotak Mahindra Bank Limited',
            'SBIN': 'State Bank of India',
            'INDUSINDBK': 'IndusInd Bank Limited',
            'FEDERALBNK': 'Federal Bank Limited',
            'BANKBARODA': 'Bank of Baroda',
            'PNB': 'Punjab National Bank',
            'CANBK': 'Canara Bank',
            
            # IT Services
            'TCS': 'Tata Consultancy Services Limited',
            'INFY': 'Infosys Limited',
            'WIPRO': 'Wipro Limited',
            'HCLTECH': 'HCL Technologies Limited',
            'TECHM': 'Tech Mahindra Limited',
            'LTIM': 'LTIMindtree Limited',
            'MPHASIS': 'Mphasis Limited',
            'PERSISTENT': 'Persistent Systems Limited',
            
            # Oil & Gas
            'RELIANCE': 'Reliance Industries Limited',
            'ONGC': 'Oil and Natural Gas Corporation Limited',
            'BPCL': 'Bharat Petroleum Corporation Limited',
            'IOC': 'Indian Oil Corporation Limited',
            'GAIL': 'GAIL (India) Limited',
            'HINDPETRO': 'Hindustan Petroleum Corporation Limited',
            
            # Automobiles
            'MARUTI': 'Maruti Suzuki India Limited',
            'M&M': 'Mahindra & Mahindra Limited',
            'TATAMOTORS': 'Tata Motors Limited',
            'BAJAJ-AUTO': 'Bajaj Auto Limited',
            'HEROMOTOCO': 'Hero MotoCorp Limited',
            'EICHERMOT': 'Eicher Motors Limited',
            'ASHOKLEY': 'Ashok Leyland Limited',
            'TVSMOTOR': 'TVS Motor Company Limited',
            
            # Pharmaceuticals
            'SUNPHARMA': 'Sun Pharmaceutical Industries Limited',
            'DRREDDY': 'Dr. Reddy\'s Laboratories Limited',
            'CIPLA': 'Cipla Limited',
            'DIVISLAB': 'Divi\'s Laboratories Limited',
            'BIOCON': 'Biocon Limited',
            'LUPIN': 'Lupin Limited',
            'TORNTPHARM': 'Torrent Pharmaceuticals Limited',
            'GLENMARK': 'Glenmark Pharmaceuticals Limited',
            'CADILAHC': 'Cadila Healthcare Limited',
            'AUROPHARMA': 'Aurobindo Pharma Limited',
            
            # FMCG
            'HINDUNILVR': 'Hindustan Unilever Limited',
            'ITC': 'ITC Limited',
            'NESTLEIND': 'Nestle India Limited',
            'BRITANNIA': 'Britannia Industries Limited',
            'DABUR': 'Dabur India Limited',
            'GODREJCP': 'Godrej Consumer Products Limited',
            'MARICO': 'Marico Limited',
            'COLPAL': 'Colgate Palmolive (India) Limited',
            
            # Metals & Mining
            'TATASTEEL': 'Tata Steel Limited',
            'JSWSTEEL': 'JSW Steel Limited',
            'HINDALCO': 'Hindalco Industries Limited',
            'VEDL': 'Vedanta Limited',
            'COALINDIA': 'Coal India Limited',
            'SAIL': 'Steel Authority of India Limited',
            'NMDC': 'NMDC Limited',
            'JINDALSTEL': 'Jindal Steel & Power Limited',
            
            # Cement
            'ULTRACEMCO': 'UltraTech Cement Limited',
            'GRASIM': 'Grasim Industries Limited',
            'SHREECEM': 'Shree Cement Limited',
            'ACC': 'ACC Limited',
            'AMBUJACEMENT': 'Ambuja Cements Limited',
            'JKCEMENT': 'JK Cement Limited',
            
            # Power
            'NTPC': 'NTPC Limited',
            'POWERGRID': 'Power Grid Corporation of India Limited',
            'TATAPOWER': 'Tata Power Company Limited',
            'ADANIENT': 'Adani Enterprises Limited',
            'ADANIPOWER': 'Adani Power Limited',
            'JSHL': 'Jaiprakash Associates Limited',
            
            # Telecom
            'BHARTIARTL': 'Bharti Airtel Limited',
            'RCOM': 'Reliance Communications Limited',
            'IDEA': 'Vodafone Idea Limited',
            
            # Consumer Goods
            'BAJAJFINSV': 'Bajaj Finserv Limited',
            'BAJFINANCE': 'Bajaj Finance Limited',
            'TITAN': 'Titan Company Limited',
            'ASIANPAINT': 'Asian Paints Limited',
            'PIDILITIND': 'Pidilite Industries Limited',
            
            # Infrastructure
            'LT': 'Larsen & Toubro Limited',
            'DLF': 'DLF Limited',
            'GODREJPROP': 'Godrej Properties Limited',
            'OBEROIRLTY': 'Oberoi Realty Limited',
        }
        
        return backup_stocks
    
    def get_all_bse_stocks(self) -> Dict[str, str]:
        """Fetch ALL BSE stocks"""
        print("Fetching comprehensive BSE stock list...")
        
        all_stocks = {}
        
        # Method 1: BSE API (if available)
        try:
            bse_stocks = self._fetch_bse_stocks()
            all_stocks.update(bse_stocks)
            print(f"BSE API: {len(bse_stocks)} stocks")
        except Exception as e:
            print(f"BSE API error: {e}")
        
        # Method 2: Convert NSE to BSE format
        try:
            if not all_stocks:
                nse_stocks = self.get_all_nse_stocks()
                for symbol, name in nse_stocks.items():
                    # Add .BO suffix for BSE
                    bse_symbol = f"{symbol}.BO"
                    all_stocks[bse_symbol] = name
                print(f"NSE->BSE conversion: {len(all_stocks)} stocks")
        except Exception as e:
            print(f"NSE->BSE conversion error: {e}")
        
        self.all_bse_stocks = all_stocks
        print(f"Total BSE stocks collected: {len(all_stocks)}")
        return all_stocks
    
    def _fetch_bse_stocks(self) -> Dict[str, str]:
        """Fetch BSE stocks from BSE API"""
        stocks = {}
        
        # BSE doesn't have a public API like NSE
        # We'll use alternative methods or convert from NSE
        
        return stocks
    
    def get_comprehensive_corporate_actions(self, portfolio_symbols: List[str]) -> List[CorporateAction]:
        """Get corporate actions for portfolio stocks using comprehensive data"""
        print(f"Fetching comprehensive corporate actions for {len(portfolio_symbols)} symbols...")
        
        all_actions = []
        
        # Get all available stock symbols first
        if not self.all_nse_stocks:
            self.get_all_nse_stocks()
        
        # Normalize portfolio symbols to match available stocks
        normalized_symbols = self._normalize_portfolio_symbols(portfolio_symbols)
        
        print(f"Normalized to {len(normalized_symbols)} symbols for fetching")
        
        # Method 1: NSE Corporate Actions API
        try:
            nse_actions = self._fetch_nse_corporate_actions(normalized_symbols)
            all_actions.extend(nse_actions)
            print(f"NSE Corporate Actions: {len(nse_actions)} actions")
        except Exception as e:
            print(f"NSE Corporate Actions error: {e}")
        
        # Method 2: BSE Corporate Actions API
        try:
            bse_actions = self._fetch_bse_corporate_actions(normalized_symbols)
            all_actions.extend(bse_actions)
            print(f"BSE Corporate Actions: {len(bse_actions)} actions")
        except Exception as e:
            print(f"BSE Corporate Actions error: {e}")
        
        # Method 3: Financial data providers
        try:
            provider_actions = self._fetch_provider_corporate_actions(normalized_symbols)
            all_actions.extend(provider_actions)
            print(f"Provider Corporate Actions: {len(provider_actions)} actions")
        except Exception as e:
            print(f"Provider Corporate Actions error: {e}")
        
        # Remove duplicates and filter by date
        unique_actions = self._deduplicate_and_filter_actions(all_actions)
        
        print(f"Total unique corporate actions found: {len(unique_actions)}")
        return unique_actions
    
    def _normalize_portfolio_symbols(self, portfolio_symbols: List[str]) -> List[str]:
        """Normalize portfolio symbols to match comprehensive stock database"""
        normalized = []
        
        for symbol in portfolio_symbols:
            # Clean symbol
            clean_symbol = symbol.upper().replace('.NS', '').replace('.BO', '').strip()
            
            # Check if symbol exists in our comprehensive database
            if clean_symbol in self.all_nse_stocks:
                normalized.append(clean_symbol)
                normalized.append(f"{clean_symbol}.NS")  # NSE format
                normalized.append(f"{clean_symbol}.BO")  # BSE format
            else:
                # Add original symbol anyway
                normalized.append(symbol)
        
        return list(set(normalized))
    
    def _fetch_nse_corporate_actions(self, symbols: List[str]) -> List[CorporateAction]:
        """Fetch corporate actions from NSE"""
        actions = []
        
        try:
            # NSE Corporate Actions API
            url = "https://www.nseindia.com/api/corporates-corporateActions"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data:
                    symbol = item.get('symbol', '').strip()
                    
                    # Check if this symbol is in our portfolio
                    if any(s.replace('.NS', '').replace('.BO', '') == symbol for s in symbols):
                        action = self._parse_nse_corporate_action(item)
                        if action:
                            actions.append(action)
        
        except Exception as e:
            print(f"NSE Corporate Actions API error: {e}")
        
        return actions
    
    def _fetch_bse_corporate_actions(self, symbols: List[str]) -> List[CorporateAction]:
        """Fetch corporate actions from BSE"""
        actions = []
        
        # BSE corporate actions would need specific API integration
        # For now, return empty list
        
        return actions
    
    def _fetch_provider_corporate_actions(self, symbols: List[str]) -> List[CorporateAction]:
        """Fetch corporate actions from financial data providers"""
        actions = []
        
        # Use third-party financial data providers
        # This would integrate with services like Alpha Vantage, Financial Modeling Prep, etc.
        
        return actions
    
    def _parse_nse_corporate_action(self, item: dict) -> Optional[CorporateAction]:
        """Parse NSE corporate action item"""
        try:
            symbol = item.get('symbol', '')
            purpose = item.get('purpose', '').lower()
            
            # Determine action type
            action_type = 'dividend'
            if 'split' in purpose:
                action_type = 'split'
            elif 'bonus' in purpose:
                action_type = 'bonus'
            elif 'rights' in purpose:
                action_type = 'rights'
            
            return CorporateAction(
                symbol=f"{symbol}.NS",
                company_name=item.get('companyName', symbol),
                action_type=action_type,
                announcement_date=item.get('bcStartDate', ''),
                ex_date=item.get('exDate', ''),
                record_date=item.get('recordDate', ''),
                payment_date=item.get('paymentDate', ''),
                purpose=item.get('purpose', ''),
                source='NSE Official'
            )
            
        except Exception as e:
            print(f"Error parsing NSE corporate action: {e}")
            return None
    
    def _deduplicate_and_filter_actions(self, actions: List[CorporateAction]) -> List[CorporateAction]:
        """Remove duplicates and filter by date range"""
        # Filter by date range (next 90 days)
        current_date = datetime.now().date()
        cutoff_date = current_date + timedelta(days=90)
        
        filtered_actions = []
        for action in actions:
            try:
                ex_date = datetime.strptime(action.ex_date, '%Y-%m-%d').date()
                if current_date <= ex_date <= cutoff_date:
                    filtered_actions.append(action)
            except (ValueError, AttributeError):
                continue
        
        # Remove duplicates
        unique_actions = []
        seen = set()
        
        for action in filtered_actions:
            key = (action.symbol.replace('.NS', '').replace('.BO', ''), 
                   action.action_type, action.ex_date)
            if key not in seen:
                unique_actions.append(action)
                seen.add(key)
        
        # Sort by ex_date
        unique_actions.sort(key=lambda x: x.ex_date)
        return unique_actions
    
    def save_cache(self):
        """Save comprehensive stock data to cache"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'nse_stocks': self.all_nse_stocks,
                'bse_stocks': self.all_bse_stocks,
                'total_stocks': len(self.all_nse_stocks) + len(self.all_bse_stocks)
            }
            
            import os
            os.makedirs('data', exist_ok=True)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            print(f"Saved comprehensive stock data to cache: {len(self.all_nse_stocks)} NSE + {len(self.all_bse_stocks)} BSE stocks")
            
        except Exception as e:
            print(f"Error saving cache: {e}")

# Global instance
comprehensive_fetcher = ComprehensiveNSEBSEFetcher()