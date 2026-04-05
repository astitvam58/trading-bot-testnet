import hmac
import hashlib
import time
from typing import Dict, Any, Optional
from decimal import Decimal
import requests
import json

from bot.logging_config import get_logger


class BinanceAPIError(Exception):
    """Custom exception for Binance API errors"""
    pass


class BinanceClient:
    """
    Wrapper for Binance Futures Testnet API.
    Supports both Market and Limit orders on USDT-M futures.
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize Binance client.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet if True, mainnet if False
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = get_logger()
        
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"
        
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "trading-bot/1.0"
        })
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate HMAC SHA256 signature for request.
        
        Args:
            params: Request parameters
        
        Returns:
            Signature string
        """
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Binance API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Request parameters
            signed: Whether request needs signature
        
        Returns:
            JSON response
        
        Raises:
            BinanceAPIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        try:
            if signed:
                params["timestamp"] = int(time.time() * 1000)
                params["signature"] = self._generate_signature(params)
                self.session.headers.update({"X-MBX-APIKEY": self.api_key})
            
            self.logger.debug(f"Request: {method} {url} with params: {params}")
            
            response = self.session.request(method, url, params=params, timeout=10)
            
            self.logger.debug(f"Response status: {response.status_code}")
            
            # Handle different status codes
            if response.status_code == 200:
                result = response.json()
                self.logger.debug(f"Response body: {json.dumps(result, indent=2)}")
                return result
            
            elif response.status_code == 400:
                error_data = response.json()
                raise BinanceAPIError(
                    f"Bad request (400): {error_data.get('msg', 'Unknown error')}"
                )
            
            elif response.status_code == 401:
                raise BinanceAPIError("Unauthorized (401): Invalid API credentials")
            
            elif response.status_code == 403:
                raise BinanceAPIError("Forbidden (403): Access denied")
            
            elif response.status_code == 429:
                raise BinanceAPIError("Rate limited (429): Too many requests")
            
            elif response.status_code == 500:
                raise BinanceAPIError("Server error (500): Binance server error")
            
            else:
                raise BinanceAPIError(
                    f"HTTP {response.status_code}: {response.text}"
                )
        
        except requests.exceptions.Timeout:
            raise BinanceAPIError("Request timeout: Connection took too long")
        except requests.exceptions.ConnectionError:
            raise BinanceAPIError("Connection error: Unable to connect to Binance")
        except json.JSONDecodeError:
            raise BinanceAPIError(f"Invalid JSON response: {response.text}")
    
    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal
    ) -> Dict[str, Any]:
        """
        Place a market order on Binance Futures.
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
        
        Returns:
            Order response from Binance
        
        Raises:
            BinanceAPIError: If order placement fails
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": str(quantity)
        }
        
        self.logger.info(f"Placing MARKET order: {side} {quantity} {symbol}")
        
        try:
            response = self._request("POST", "/fapi/v1/order", params, signed=True)
            self.logger.info(f"Market order placed successfully: {response}")
            return response
        except BinanceAPIError as e:
            self.logger.error(f"Failed to place market order: {str(e)}")
            raise
    
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        price: Decimal
    ) -> Dict[str, Any]:
        """
        Place a limit order on Binance Futures.
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            price: Limit price
        
        Returns:
            Order response from Binance
        
        Raises:
            BinanceAPIError: If order placement fails
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "timeInForce": "GTC",  # Good-Till-Cancelled
            "quantity": str(quantity),
            "price": str(price)
        }
        
        self.logger.info(
            f"Placing LIMIT order: {side} {quantity} {symbol} @ {price}"
        )
        
        try:
            response = self._request("POST", "/fapi/v1/order", params, signed=True)
            self.logger.info(f"Limit order placed successfully: {response}")
            return response
        except BinanceAPIError as e:
            self.logger.error(f"Failed to place limit order: {str(e)}")
            raise
    
    def place_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        price: Decimal,
        stop_price: Decimal
    ) -> Dict[str, Any]:
        """
        Place a stop-limit order on Binance Futures (BONUS FEATURE).
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            price: Limit price
            stop_price: Stop price
        
        Returns:
            Order response from Binance
        
        Raises:
            BinanceAPIError: If order placement fails
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": "STOP",
            "timeInForce": "GTC",
            "quantity": str(quantity),
            "price": str(price),
            "stopPrice": str(stop_price)
        }
        
        self.logger.info(
            f"Placing STOP-LIMIT order: {side} {quantity} {symbol} "
            f"@ {price} (stop @ {stop_price})"
        )
        
        try:
            response = self._request("POST", "/fapi/v1/order", params, signed=True)
            self.logger.info(f"Stop-limit order placed successfully: {response}")
            return response
        except BinanceAPIError as e:
            self.logger.error(f"Failed to place stop-limit order: {str(e)}")
            raise
    
    def get_order_status(
        self,
        symbol: str,
        order_id: int
    ) -> Dict[str, Any]:
        """
        Get the status of a placed order.
        
        Args:
            symbol: Trading pair
            order_id: Order ID
        
        Returns:
            Order details
        
        Raises:
            BinanceAPIError: If request fails
        """
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        
        self.logger.debug(f"Fetching order status for {symbol} order {order_id}")
        
        try:
            response = self._request("GET", "/fapi/v1/order", params, signed=True)
            return response
        except BinanceAPIError as e:
            self.logger.error(f"Failed to get order status: {str(e)}")
            raise
    
    def close(self):
        """Close the session."""
        self.session.close()
        self.logger.debug("Session closed")
