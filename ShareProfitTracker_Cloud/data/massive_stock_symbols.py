"""
Massive Stock Symbol Database with 2000+ Indian Stocks
Comprehensive coverage of NSE and BSE stocks for complete market coverage
"""

import json
import os
from typing import Dict, List, Tuple

def load_massive_stock_database() -> Dict[str, str]:
    """Load the massive stock database from our comprehensive cache"""
    try:
        # Try to load from massive database first
        massive_db_path = os.path.join(os.path.dirname(__file__), 'massive_stocks_2000plus.json')
        if os.path.exists(massive_db_path):
            with open(massive_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                nse_stocks = data.get('nse_stocks', {})
                return {f"{symbol}.NS": company for symbol, company in nse_stocks.items()}

        # Fallback to ultra comprehensive
        ultra_db_path = os.path.join(os.path.dirname(__file__), 'ultra_comprehensive_stocks.json')
        if os.path.exists(ultra_db_path):
            with open(ultra_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                nse_stocks = data.get('nse_stocks', {})
                return {f"{symbol}.NS": company for symbol, company in nse_stocks.items()}

        # Final fallback to complete indian stocks
        complete_db_path = os.path.join(os.path.dirname(__file__), 'complete_indian_stocks.json')
        if os.path.exists(complete_db_path):
            with open(complete_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                nse_stocks = data.get('nse_stocks', {})
                return {f"{symbol}.NS": company for symbol, company in nse_stocks.items()}

    except Exception as e:
        print(f"Error loading massive stock database: {e}")

    # Ultimate fallback - popular stocks
    return get_popular_fallback_stocks()

def get_popular_fallback_stocks() -> Dict[str, str]:
    """Fallback popular stocks in case database loading fails"""
    return {
        "RELIANCE.NS": "Reliance Industries Limited",
        "TCS.NS": "Tata Consultancy Services Limited",
        "HDFCBANK.NS": "HDFC Bank Limited",
        "INFY.NS": "Infosys Limited",
        "HINDUNILVR.NS": "Hindustan Unilever Limited",
        "ICICIBANK.NS": "ICICI Bank Limited",
        "SBIN.NS": "State Bank of India",
        "BHARTIARTL.NS": "Bharti Airtel Limited",
        "ITC.NS": "ITC Limited",
        "KOTAKBANK.NS": "Kotak Mahindra Bank Limited",
        "LT.NS": "Larsen & Toubro Limited",
        "AXISBANK.NS": "Axis Bank Limited",
        "MARUTI.NS": "Maruti Suzuki India Limited",
        "HCLTECH.NS": "HCL Technologies Limited",
        "WIPRO.NS": "Wipro Limited",
        "ULTRACEMCO.NS": "UltraTech Cement Limited",
        "TITAN.NS": "Titan Company Limited",
        "SUNPHARMA.NS": "Sun Pharmaceutical Industries Limited",
        "POWERGRID.NS": "Power Grid Corporation of India Limited",
        "NESTLEIND.NS": "Nestle India Limited",
        "ADANIPORTS.NS": "Adani Ports and Special Economic Zone Limited",
        "NTPC.NS": "NTPC Limited",
        "TECHM.NS": "Tech Mahindra Limited",
        "ONGC.NS": "Oil and Natural Gas Corporation Limited",
        "JSWSTEEL.NS": "JSW Steel Limited",
        "TATAMOTORS.NS": "Tata Motors Limited",
        "COALINDIA.NS": "Coal India Limited",
        "DIVISLAB.NS": "Divi's Laboratories Limited",
        "BAJFINANCE.NS": "Bajaj Finance Limited",
        "DRREDDY.NS": "Dr. Reddy's Laboratories Limited",
        "GRASIM.NS": "Grasim Industries Limited",
        "TATASTEEL.NS": "Tata Steel Limited",
        "EICHERMOT.NS": "Eicher Motors Limited",
        "HEROMOTOCO.NS": "Hero MotoCorp Limited",
        "CIPLA.NS": "Cipla Limited",
        "BRITANNIA.NS": "Britannia Industries Limited",
        "HINDALCO.NS": "Hindalco Industries Limited",
        "BPCL.NS": "Bharat Petroleum Corporation Limited",
        "SHREECEM.NS": "Shree Cement Limited",
        "BAJAJ-AUTO.NS": "Bajaj Auto Limited",
        "IOC.NS": "Indian Oil Corporation Limited",
        "INDUSINDBK.NS": "IndusInd Bank Limited",
        "ADANIENT.NS": "Adani Enterprises Limited",
        "TATACONSUM.NS": "Tata Consumer Products Limited",
        "GODREJCP.NS": "Godrej Consumer Products Limited",
        "SBILIFE.NS": "SBI Life Insurance Company Limited",
        # Additional popular stocks from your portfolio and others
        "VEDL.NS": "Vedanta Limited",
        "GLENMARK.NS": "Glenmark Pharmaceuticals Limited",
        "PERSISTENT.NS": "Persistent Systems Limited",
        "MPHASIS.NS": "Mphasis Limited",
        "COFORGE.NS": "Coforge Limited",
        "MASTEK.NS": "Mastek Limited",
        "GENUSPOWER.NS": "Genus Power Infrastructures Limited",
        "MAPMYINDIA.NS": "CE Info Systems Limited",
        "PAISALO.NS": "Paisalo Digital Limited",
        "SYRMA.NS": "Syrma SGS Technology Limited",
        "COCHINSHIP.NS": "Cochin Shipyard Limited",
        "ZOMATO.NS": "Zomato Limited",
        "PAYTM.NS": "One 97 Communications Limited",
        "NYKAA.NS": "FSN E-Commerce Ventures Limited",
        "POLICYBZR.NS": "PB Fintech Limited"
    }

# Load the massive database
print("Loading massive stock database...")
INDIAN_STOCKS = load_massive_stock_database()
print(f"Loaded {len(INDIAN_STOCKS)} Indian stocks from massive database")

# Popular US Stocks (for international investors)
US_STOCKS = {
    "AAPL": "Apple Inc.",
    "GOOGL": "Alphabet Inc. (Google)",
    "MSFT": "Microsoft Corporation",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms Inc. (Facebook)",
    "NFLX": "Netflix Inc.",
    "ORCL": "Oracle Corporation",
    "CRM": "Salesforce Inc.",
    "ADBE": "Adobe Inc.",
    "PYPL": "PayPal Holdings Inc.",
    "INTC": "Intel Corporation",
    "CSCO": "Cisco Systems Inc.",
    "PEP": "PepsiCo Inc.",
    "KO": "The Coca-Cola Company",
    "DIS": "The Walt Disney Company",
    "BA": "The Boeing Company",
    "JNJ": "Johnson & Johnson",
    "V": "Visa Inc.",
}

# Combined database for easy searching
ALL_STOCKS = {**INDIAN_STOCKS, **US_STOCKS}

def search_stocks(query: str, limit: int = 20) -> List[Tuple[str, str]]:
    """
    Enhanced search for stocks by symbol or company name
    Returns list of (symbol, company_name) tuples
    """
    if not query or len(query.strip()) == 0:
        # Return popular stocks for empty query
        popular = list(INDIAN_STOCKS.items())[:limit]
        return popular

    query = query.upper().strip()
    matches = []

    # Priority 1: Exact symbol matches
    for symbol, company in ALL_STOCKS.items():
        if symbol.upper() == query:
            matches.append((symbol, company))
            if len(matches) >= limit:
                return matches

    # Priority 2: Symbol starts with query
    for symbol, company in ALL_STOCKS.items():
        if symbol.upper().startswith(query) and (symbol, company) not in matches:
            matches.append((symbol, company))
            if len(matches) >= limit:
                return matches

    # Priority 3: Symbol contains query
    for symbol, company in ALL_STOCKS.items():
        if query in symbol.upper() and (symbol, company) not in matches:
            matches.append((symbol, company))
            if len(matches) >= limit:
                return matches

    # Priority 4: Company name contains query
    for symbol, company in ALL_STOCKS.items():
        if query in company.upper() and (symbol, company) not in matches:
            matches.append((symbol, company))
            if len(matches) >= limit:
                return matches

    return matches[:limit]

def get_popular_indian_stocks(limit: int = 50):
    """Get list of popular Indian stocks for suggestions"""
    popular_symbols = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
        "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
        "LT.NS", "AXISBANK.NS", "MARUTI.NS", "HCLTECH.NS", "WIPRO.NS",
        "PERSISTENT.NS", "MASTEK.NS", "GLENMARK.NS", "VEDL.NS", "GENUSPOWER.NS",
        "MAPMYINDIA.NS", "PAISALO.NS", "SYRMA.NS", "COCHINSHIP.NS", "ZOMATO.NS"
    ]

    popular = []
    for symbol in popular_symbols:
        if symbol in INDIAN_STOCKS:
            popular.append((symbol, INDIAN_STOCKS[symbol]))
        if len(popular) >= limit:
            break

    # If we don't have enough, add more from the database
    if len(popular) < limit:
        remaining = limit - len(popular)
        for symbol, company in list(INDIAN_STOCKS.items())[len(popular):len(popular) + remaining]:
            if (symbol, company) not in popular:
                popular.append((symbol, company))

    return popular

def get_company_name(symbol: str) -> str:
    """Get company name for a given symbol"""
    return ALL_STOCKS.get(symbol.upper(), symbol)

def get_all_indian_stocks() -> Dict[str, str]:
    """Get all Indian stocks in the database"""
    return INDIAN_STOCKS.copy()

def get_stock_count() -> int:
    """Get total number of stocks in database"""
    return len(INDIAN_STOCKS)

# Print database info when module loads
if INDIAN_STOCKS:
    stock_count = len(INDIAN_STOCKS)
    if stock_count >= 1000:
        print(f"[SUCCESS] Massive stock database loaded: {stock_count:,} stocks available for selection!")
    elif stock_count >= 500:
        print(f"[GOOD] Comprehensive stock database loaded: {stock_count} stocks available!")
    else:
        print(f"[FALLBACK] Using fallback stock database: {stock_count} popular stocks available.")
else:
    print("[ERROR] Failed to load stock database - using minimal fallback.")