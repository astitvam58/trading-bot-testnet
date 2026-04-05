from enum import Enum
from typing import Tuple
from decimal import Decimal


class OrderSide(str, Enum):
    """Valid order sides"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Valid order types"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_symbol(symbol: str) -> str:
    """
    Validate trading pair symbol.
    
    Args:
        symbol: Trading pair (e.g., BTCUSDT)
    
    Returns:
        Normalized symbol (uppercase)
    
    Raises:
        ValidationError: If symbol is invalid
    """
    if not symbol:
        raise ValidationError("Symbol cannot be empty")
    
    symbol = symbol.strip().upper()
    
    # Basic validation: should be alphanumeric
    if not symbol.isalnum():
        raise ValidationError(f"Invalid symbol: {symbol}. Must be alphanumeric.")
    
    if len(symbol) < 3:
        raise ValidationError(f"Symbol too short: {symbol}")
    
    return symbol


def validate_side(side: str) -> OrderSide:
    """
    Validate order side.
    
    Args:
        side: BUY or SELL
    
    Returns:
        OrderSide enum
    
    Raises:
        ValidationError: If side is invalid
    """
    side_upper = side.strip().upper()
    
    try:
        return OrderSide[side_upper]
    except KeyError:
        raise ValidationError(
            f"Invalid side: {side}. Must be BUY or SELL."
        )


def validate_order_type(order_type: str) -> OrderType:
    """
    Validate order type.
    
    Args:
        order_type: MARKET or LIMIT
    
    Returns:
        OrderType enum
    
    Raises:
        ValidationError: If order type is invalid
    """
    order_type_upper = order_type.strip().upper()
    
    try:
        return OrderType[order_type_upper]
    except KeyError:
        raise ValidationError(
            f"Invalid order type: {order_type}. Must be MARKET or LIMIT."
        )


def validate_quantity(quantity: str) -> Decimal:
    """
    Validate order quantity.
    
    Args:
        quantity: Order quantity as string
    
    Returns:
        Decimal quantity
    
    Raises:
        ValidationError: If quantity is invalid
    """
    try:
        qty = Decimal(quantity)
    except Exception:
        raise ValidationError(f"Invalid quantity: {quantity}. Must be a valid number.")
    
    if qty <= 0:
        raise ValidationError(f"Quantity must be positive, got {qty}")
    
    return qty


def validate_price(price: str) -> Decimal:
    """
    Validate order price.
    
    Args:
        price: Order price as string
    
    Returns:
        Decimal price
    
    Raises:
        ValidationError: If price is invalid
    """
    try:
        p = Decimal(price)
    except Exception:
        raise ValidationError(f"Invalid price: {price}. Must be a valid number.")
    
    if p <= 0:
        raise ValidationError(f"Price must be positive, got {p}")
    
    return p


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str = None
) -> Tuple[str, OrderSide, OrderType, Decimal, Decimal]:
    """
    Validate all order parameters together.
    
    Args:
        symbol: Trading pair
        side: BUY or SELL
        order_type: MARKET or LIMIT
        quantity: Order quantity
        price: Order price (required for LIMIT)
    
    Returns:
        Tuple of validated parameters
    
    Raises:
        ValidationError: If any parameter is invalid
    """
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_order_type = validate_order_type(order_type)
    validated_quantity = validate_quantity(quantity)
    
    if validated_order_type == OrderType.LIMIT:
        if price is None:
            raise ValidationError("Price is required for LIMIT orders")
        validated_price = validate_price(price)
    else:
        validated_price = None
    
    return validated_symbol, validated_side, validated_order_type, validated_quantity, validated_price
