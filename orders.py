from decimal import Decimal
from typing import Dict, Any, Optional

from bot.client import BinanceClient, BinanceAPIError
from bot.validators import OrderSide, OrderType
from bot.logging_config import get_logger


class OrderManager:
    """Manages order placement and status tracking."""
    
    def __init__(self, client: BinanceClient):
        """
        Initialize OrderManager.
        
        Args:
            client: BinanceClient instance
        """
        self.client = client
        self.logger = get_logger()
    
    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: Decimal,
        price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Place an order with the specified parameters.
        
        Args:
            symbol: Trading pair
            side: OrderSide (BUY/SELL)
            order_type: OrderType (MARKET/LIMIT/STOP_LIMIT)
            quantity: Order quantity
            price: Price (required for LIMIT/STOP_LIMIT)
            stop_price: Stop price (required for STOP_LIMIT)
        
        Returns:
            Order response from Binance
        
        Raises:
            BinanceAPIError: If order placement fails
            ValueError: If parameters are invalid for order type
        """
        try:
            if order_type == OrderType.MARKET:
                self.logger.info(
                    f"Executing MARKET order: {side.value} {quantity} {symbol}"
                )
                return self.client.place_market_order(
                    symbol=symbol,
                    side=side.value,
                    quantity=quantity
                )
            
            elif order_type == OrderType.LIMIT:
                if price is None:
                    raise ValueError("Price is required for LIMIT orders")
                
                self.logger.info(
                    f"Executing LIMIT order: {side.value} {quantity} {symbol} @ {price}"
                )
                return self.client.place_limit_order(
                    symbol=symbol,
                    side=side.value,
                    quantity=quantity,
                    price=price
                )
            
            else:
                raise ValueError(f"Unknown order type: {order_type}")
        
        except BinanceAPIError as e:
            self.logger.error(f"Binance API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error placing order: {str(e)}")
            raise
    
    def place_stop_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: Decimal,
        price: Decimal,
        stop_price: Decimal
    ) -> Dict[str, Any]:
        """
        Place a stop-limit order (BONUS FEATURE).
        
        Args:
            symbol: Trading pair
            side: OrderSide (BUY/SELL)
            quantity: Order quantity
            price: Limit price
            stop_price: Stop price
        
        Returns:
            Order response from Binance
        
        Raises:
            BinanceAPIError: If order placement fails
        """
        try:
            self.logger.info(
                f"Executing STOP-LIMIT order: {side.value} {quantity} {symbol} "
                f"@ {price} (stop @ {stop_price})"
            )
            return self.client.place_stop_limit_order(
                symbol=symbol,
                side=side.value,
                quantity=quantity,
                price=price,
                stop_price=stop_price
            )
        except BinanceAPIError as e:
            self.logger.error(f"Binance API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error placing stop-limit order: {str(e)}")
            raise
    
    def format_order_response(
        self,
        response: Dict[str, Any]
    ) -> str:
        """
        Format order response for display.
        
        Args:
            response: Order response from Binance
        
        Returns:
            Formatted string representation
        """
        lines = [
            "\n" + "=" * 60,
            "ORDER PLACED SUCCESSFULLY",
            "=" * 60,
            f"Order ID:           {response.get('orderId')}",
            f"Symbol:             {response.get('symbol')}",
            f"Side:               {response.get('side')}",
            f"Type:               {response.get('type')}",
            f"Status:             {response.get('status')}",
            f"Quantity:           {response.get('origQty')}",
            f"Executed Qty:       {response.get('executedQty')}",
            f"Price:              {response.get('price')}",
        ]
        
        # Add average price if order was partially/fully filled
        avg_price = response.get('avgPrice')
        if avg_price and float(avg_price) > 0:
            lines.append(f"Average Price:      {avg_price}")
        
        # Add cumulative quote amount if available
        cum_quote = response.get('cumQuote')
        if cum_quote:
            lines.append(f"Cumulative Quote:   {cum_quote}")
        
        # Add time info
        if 'updateTime' in response:
            lines.append(f"Update Time:        {response['updateTime']}")
        
        lines.append("=" * 60 + "\n")
        
        return "\n".join(lines)
