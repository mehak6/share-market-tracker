"""
Improved Price Fetcher with proper logging and error handling
"""
try:
    import yfinance as yf
    MOCK_MODE = False
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        import mock_yfinance as yf
        MOCK_MODE = True
    except ImportError:
        yf = None
        MOCK_MODE = True

import requests
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
import time

try:
    from utils.logger import get_logger
    from config.constants import (
        API_RATE_LIMIT_SECONDS,
        API_RETRY_ATTEMPTS,
        API_TIMEOUT_SECONDS,
        API_BATCH_THRESHOLD
    )
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)
    API_RATE_LIMIT_SECONDS = 0.1
    API_RETRY_ATTEMPTS = 3
    API_TIMEOUT_SECONDS = 10
    API_BATCH_THRESHOLD = 5

logger = get_logger(__name__)


class PriceFetchError(Exception):
    """Custom exception for price fetching errors"""
    pass


class PriceFetcher:
    """
    Improved price fetcher with:
    - Proper logging
    - Specific exception handling
    - Retry logic
    - Better error messages
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = API_TIMEOUT_SECONDS
        self.last_request_time = 0
        self.min_request_interval = API_RATE_LIMIT_SECONDS

        if MOCK_MODE:
            logger.warning("Running in MOCK MODE - install yfinance for real market data")
            logger.info("To install: pip install yfinance")
        else:
            logger.info("PriceFetcher initialized with real market data")

    def _rate_limit(self):
        """
        Apply rate limiting between API requests

        Ensures minimum time interval between consecutive requests
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.3f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _extract_price_from_info(self, info: dict) -> Optional[float]:
        """
        Extract price from ticker info dictionary

        Args:
            info: Ticker info dictionary from yfinance

        Returns:
            Price as float, or None if not found
        """
        # Try different price fields in order of preference
        price_fields = [
            'currentPrice',
            'regularMarketPrice',
            'previousClose',
            'ask',
            'bid',
            'lastPrice'
        ]

        for field in price_fields:
            if field in info and info[field] is not None:
                try:
                    price = float(info[field])
                    if price > 0:  # Sanity check
                        logger.debug(f"Extracted price from field '{field}': ₹{price}")
                        return price
                except (ValueError, TypeError) as e:
                    logger.debug(f"Invalid price in field '{field}': {e}")
                    continue

        return None

    def get_current_price(self, symbol: str, retry_count: int = 0) -> Optional[float]:
        """
        Get current price for a single stock symbol

        Args:
            symbol: Stock ticker symbol (e.g., 'RELIANCE.NS')
            retry_count: Current retry attempt (internal use)

        Returns:
            Current price as float, or None if unavailable

        Raises:
            PriceFetchError: If symbol is invalid or request fails critically
        """
        if not symbol or not isinstance(symbol, str):
            raise PriceFetchError(f"Invalid symbol: {symbol}")

        symbol = symbol.strip().upper()

        if yf is None:
            logger.error("yfinance not available and no mock implementation")
            return None

        try:
            self._rate_limit()
            logger.debug(f"Fetching price for {symbol}")

            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                logger.warning(f"No info returned for {symbol}")
                return None

            price = self._extract_price_from_info(info)

            if price is not None:
                logger.info(f"Fetched price for {symbol}: ₹{price:.2f}")
                return price
            else:
                logger.warning(f"No valid price fields found for {symbol}")
                return None

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout fetching price for {symbol}: {e}")
            if retry_count < API_RETRY_ATTEMPTS:
                logger.info(f"Retrying {symbol} (attempt {retry_count + 1}/{API_RETRY_ATTEMPTS})")
                time.sleep(1 * (retry_count + 1))  # Exponential backoff
                return self.get_current_price(symbol, retry_count + 1)
            return None

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error fetching price for {symbol}: {e}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching price for {symbol}: {e}")
            return None

        except ValueError as e:
            logger.error(f"Value error parsing price for {symbol}: {e}")
            return None

        except Exception as e:
            logger.exception(f"Unexpected error fetching price for {symbol}: {e}")
            return None

    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Optional[float]]:
        """
        Get prices for multiple stocks efficiently

        Args:
            symbols: List of stock ticker symbols

        Returns:
            Dictionary mapping symbols to prices (or None if unavailable)
        """
        if not symbols:
            logger.warning("get_multiple_prices called with empty symbol list")
            return {}

        # Remove duplicates and validate
        symbols = list(set(s.strip().upper() for s in symbols if s and s.strip()))

        if not symbols:
            logger.warning("No valid symbols after filtering")
            return {}

        logger.info(f"Fetching prices for {len(symbols)} symbols")

        prices = {}

        # Use batch fetching for many symbols
        if len(symbols) > API_BATCH_THRESHOLD:
            prices = self._batch_fetch(symbols)
        else:
            # Individual fetching for few symbols
            for symbol in symbols:
                prices[symbol] = self.get_current_price(symbol)

        # Log summary
        successful = sum(1 for p in prices.values() if p is not None)
        logger.info(f"Successfully fetched {successful}/{len(symbols)} prices")

        return prices

    def _batch_fetch(self, symbols: List[str]) -> Dict[str, Optional[float]]:
        """
        Fetch multiple prices in a single batch request

        Args:
            symbols: List of symbols to fetch

        Returns:
            Dictionary mapping symbols to prices
        """
        prices = {}

        try:
            logger.debug(f"Batch fetching {len(symbols)} symbols")

            # Create space-separated symbol string
            symbols_str = " ".join(symbols)
            tickers = yf.Tickers(symbols_str)

            for symbol in symbols:
                try:
                    ticker = tickers.tickers.get(symbol)
                    if ticker is None:
                        logger.warning(f"Symbol {symbol} not found in batch result")
                        prices[symbol] = None
                        continue

                    info = ticker.info
                    price = self._extract_price_from_info(info)
                    prices[symbol] = price

                    if price is not None:
                        logger.debug(f"Batch: {symbol} = ₹{price:.2f}")
                    else:
                        logger.debug(f"Batch: {symbol} = No price")

                except Exception as e:
                    logger.error(f"Error processing {symbol} in batch: {e}")
                    prices[symbol] = None

        except Exception as e:
            logger.exception(f"Batch fetch failed, falling back to individual requests: {e}")

            # Fallback to individual requests
            for symbol in symbols:
                prices[symbol] = self.get_current_price(symbol)
                time.sleep(0.1)  # Small delay between fallback requests

        return prices

    def get_company_name(self, symbol: str) -> Optional[str]:
        """
        Get company name for a stock symbol

        Args:
            symbol: Stock ticker symbol

        Returns:
            Company name, or symbol as fallback
        """
        if not symbol or not isinstance(symbol, str):
            logger.error(f"Invalid symbol for company name: {symbol}")
            return symbol

        symbol = symbol.strip().upper()

        if yf is None:
            return symbol

        try:
            self._rate_limit()
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Try different name fields
            name_fields = ['longName', 'shortName', 'displayName', 'name']

            for field in name_fields:
                if field in info and info[field]:
                    name = str(info[field])
                    logger.debug(f"Company name for {symbol}: {name}")
                    return name

            logger.warning(f"No company name found for {symbol}, using symbol")
            return symbol

        except Exception as e:
            logger.error(f"Error fetching company name for {symbol}: {e}")
            return symbol

    def validate_symbol(self, symbol: str) -> Tuple[bool, str]:
        """
        Validate if a stock symbol exists

        Args:
            symbol: Stock ticker symbol

        Returns:
            Tuple of (is_valid, message)
        """
        if not symbol or not isinstance(symbol, str):
            return False, "Symbol must be a non-empty string"

        symbol = symbol.strip().upper()

        if not symbol:
            return False, "Symbol cannot be empty"

        if yf is None:
            return True, "Cannot validate (yfinance not available)"

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or len(info) < 2:
                return False, f"Symbol '{symbol}' not found"

            # Check if it has basic required fields
            if 'symbol' not in info and 'shortName' not in info:
                return False, f"Symbol '{symbol}' appears invalid"

            logger.info(f"Symbol {symbol} validated successfully")
            return True, "Valid symbol"

        except Exception as e:
            logger.error(f"Error validating symbol {symbol}: {e}")
            return False, f"Validation failed: {str(e)}"

    def is_market_open(self) -> bool:
        """
        Check if market is currently open (heuristic)

        Returns:
            True if market is likely open, False otherwise
        """
        try:
            now = datetime.now()

            # Weekend check
            if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
                logger.debug("Market closed: Weekend")
                return False

            # Rough market hours check (9:30 AM - 4:00 PM ET for US)
            # For Indian market: 9:15 AM - 3:30 PM IST
            # This is a simplified check
            market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)

            is_open = market_open <= now <= market_close

            logger.debug(f"Market open check: {is_open}")
            return is_open

        except Exception as e:
            logger.error(f"Error checking market hours: {e}")
            # Default to assuming market is open during weekdays
            return datetime.now().weekday() < 5
