import os
import sys
from decimal import Decimal
from typing import Optional

import click
from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceAPIError
from bot.orders import OrderManager
from bot.validators import (
    validate_order_params,
    ValidationError,
    OrderSide,
    OrderType
)
from bot.logging_config import setup_logging, get_logger


# Load environment variables
load_dotenv()

# Setup logging on import
setup_logging()
logger = get_logger()


def get_api_credentials() -> tuple:
    """
    Get API credentials from environment variables.
    
    Returns:
        Tuple of (api_key, api_secret)
    
    Raises:
        click.ClickException: If credentials are missing
    """
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        raise click.ClickException(
            "Missing Binance API credentials. Set BINANCE_API_KEY and "
            "BINANCE_API_SECRET environment variables in .env file"
        )
    
    return api_key, api_secret


@click.group()
def cli():
    """Trading Bot CLI - Place orders on Binance Futures Testnet"""
    pass


@cli.command()
@click.option(
    "--symbol",
    prompt="Trading symbol (e.g., BTCUSDT)",
    help="The trading pair symbol"
)
@click.option(
    "--side",
    type=click.Choice(["BUY", "SELL"], case_sensitive=False),
    prompt="Order side (BUY/SELL)",
    help="Buy or sell"
)
@click.option(
    "--quantity",
    prompt="Order quantity",
    help="Amount to trade"
)
def market(symbol: str, side: str, quantity: str):
    """Place a MARKET order"""
    try:
        # Validate inputs
        symbol, validated_side, _, validated_qty, _ = validate_order_params(
            symbol=symbol,
            side=side,
            order_type="MARKET",
            quantity=quantity
        )
        
        # Get API credentials
        api_key, api_secret = get_api_credentials()
        
        # Create client and manager
        client = BinanceClient(api_key, api_secret, testnet=True)
        manager = OrderManager(client)
        
        # Log order request
        logger.info(
            f"Market order request - Symbol: {symbol}, Side: {validated_side.value}, "
            f"Quantity: {validated_qty}"
        )
        
        # Place order
        response = manager.place_order(
            symbol=symbol,
            side=validated_side,
            order_type=OrderType.MARKET,
            quantity=validated_qty
        )
        
        # Display formatted response
        click.echo(manager.format_order_response(response))
        
        # Log success
        logger.info(f"Market order placed successfully - Order ID: {response.get('orderId')}")
        
        client.close()
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        click.secho(f"❌ Validation Error: {str(e)}", fg="red")
        sys.exit(1)
    
    except BinanceAPIError as e:
        logger.error(f"Binance API error: {str(e)}")
        click.secho(f"❌ API Error: {str(e)}", fg="red")
        sys.exit(1)
    
    except click.ClickException:
        raise
    
    except Exception as e:
        logger.exception(f"Unexpected error in market order: {str(e)}")
        click.secho(f"❌ Error: {str(e)}", fg="red")
        sys.exit(1)


@cli.command()
@click.option(
    "--symbol",
    prompt="Trading symbol (e.g., BTCUSDT)",
    help="The trading pair symbol"
)
@click.option(
    "--side",
    type=click.Choice(["BUY", "SELL"], case_sensitive=False),
    prompt="Order side (BUY/SELL)",
    help="Buy or sell"
)
@click.option(
    "--quantity",
    prompt="Order quantity",
    help="Amount to trade"
)
@click.option(
    "--price",
    prompt="Limit price",
    help="Price at which to limit the order"
)
def limit(symbol: str, side: str, quantity: str, price: str):
    """Place a LIMIT order"""
    try:
        # Validate inputs
        symbol, validated_side, _, validated_qty, validated_price = validate_order_params(
            symbol=symbol,
            side=side,
            order_type="LIMIT",
            quantity=quantity,
            price=price
        )
        
        # Get API credentials
        api_key, api_secret = get_api_credentials()
        
        # Create client and manager
        client = BinanceClient(api_key, api_secret, testnet=True)
        manager = OrderManager(client)
        
        # Log order request
        logger.info(
            f"Limit order request - Symbol: {symbol}, Side: {validated_side.value}, "
            f"Quantity: {validated_qty}, Price: {validated_price}"
        )
        
        # Place order
        response = manager.place_order(
            symbol=symbol,
            side=validated_side,
            order_type=OrderType.LIMIT,
            quantity=validated_qty,
            price=validated_price
        )
        
        # Display formatted response
        click.echo(manager.format_order_response(response))
        
        # Log success
        logger.info(f"Limit order placed successfully - Order ID: {response.get('orderId')}")
        
        client.close()
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        click.secho(f"❌ Validation Error: {str(e)}", fg="red")
        sys.exit(1)
    
    except BinanceAPIError as e:
        logger.error(f"Binance API error: {str(e)}")
        click.secho(f"❌ API Error: {str(e)}", fg="red")
        sys.exit(1)
    
    except click.ClickException:
        raise
    
    except Exception as e:
        logger.exception(f"Unexpected error in limit order: {str(e)}")
        click.secho(f"❌ Error: {str(e)}", fg="red")
        sys.exit(1)


@cli.command()
@click.option(
    "--symbol",
    prompt="Trading symbol (e.g., BTCUSDT)",
    help="The trading pair symbol"
)
@click.option(
    "--side",
    type=click.Choice(["BUY", "SELL"], case_sensitive=False),
    prompt="Order side (BUY/SELL)",
    help="Buy or sell"
)
@click.option(
    "--quantity",
    prompt="Order quantity",
    help="Amount to trade"
)
@click.option(
    "--price",
    prompt="Limit price",
    help="Price at which to limit the order"
)
@click.option(
    "--stop-price",
    prompt="Stop price",
    help="Price at which to trigger the order"
)
def stop_limit(symbol: str, side: str, quantity: str, price: str, stop_price: str):
    """Place a STOP-LIMIT order (BONUS)"""
    try:
        # Validate basic params
        symbol, validated_side, _, validated_qty, validated_price = validate_order_params(
            symbol=symbol,
            side=side,
            order_type="LIMIT",
            quantity=quantity,
            price=price
        )
        
        # Validate stop price
        from bot.validators import validate_price
        validated_stop_price = validate_price(stop_price)
        
        # Get API credentials
        api_key, api_secret = get_api_credentials()
        
        # Create client and manager
        client = BinanceClient(api_key, api_secret, testnet=True)
        manager = OrderManager(client)
        
        # Log order request
        logger.info(
            f"Stop-limit order request - Symbol: {symbol}, Side: {validated_side.value}, "
            f"Quantity: {validated_qty}, Price: {validated_price}, Stop: {validated_stop_price}"
        )
        
        # Place order
        response = manager.place_stop_limit_order(
            symbol=symbol,
            side=validated_side,
            quantity=validated_qty,
            price=validated_price,
            stop_price=validated_stop_price
        )
        
        # Display formatted response
        click.echo(manager.format_order_response(response))
        
        # Log success
        logger.info(f"Stop-limit order placed successfully - Order ID: {response.get('orderId')}")
        
        client.close()
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        click.secho(f"❌ Validation Error: {str(e)}", fg="red")
        sys.exit(1)
    
    except BinanceAPIError as e:
        logger.error(f"Binance API error: {str(e)}")
        click.secho(f"❌ API Error: {str(e)}", fg="red")
        sys.exit(1)
    
    except click.ClickException:
        raise
    
    except Exception as e:
        logger.exception(f"Unexpected error in stop-limit order: {str(e)}")
        click.secho(f"❌ Error: {str(e)}", fg="red")
        sys.exit(1)


@cli.command()
def interactive():
    """Interactive menu-driven mode (BONUS)"""
    try:
        click.secho("\n" + "=" * 60, fg="cyan")
        click.secho("Binance Futures Trading Bot - Interactive Mode", fg="cyan", bold=True)
        click.secho("=" * 60 + "\n", fg="cyan")
        
        # Get API credentials
        api_key, api_secret = get_api_credentials()
        client = BinanceClient(api_key, api_secret, testnet=True)
        manager = OrderManager(client)
        
        while True:
            click.secho("\nSelect order type:", fg="yellow")
            click.echo("1. Market Order")
            click.echo("2. Limit Order")
            click.echo("3. Stop-Limit Order")
            click.echo("4. Exit")
            
            choice = click.prompt("Enter choice", type=int)
            
            if choice == 4:
                click.secho("\nGoodbye!", fg="green")
                break
            
            if choice not in [1, 2, 3]:
                click.secho("Invalid choice. Please try again.", fg="red")
                continue
            
            # Get common parameters
            symbol = click.prompt("Symbol (e.g., BTCUSDT)")
            side = click.prompt("Side (BUY/SELL)")
            quantity = click.prompt("Quantity")
            
            try:
                symbol, validated_side, _, validated_qty, _ = validate_order_params(
                    symbol=symbol,
                    side=side,
                    order_type="MARKET",
                    quantity=quantity
                )
            except ValidationError as e:
                click.secho(f"❌ Validation Error: {str(e)}", fg="red")
                continue
            
            try:
                if choice == 1:
                    # Market order
                    logger.info(f"Interactive market order - {symbol} {side} {quantity}")
                    response = manager.place_order(
                        symbol=symbol,
                        side=validated_side,
                        order_type=OrderType.MARKET,
                        quantity=validated_qty
                    )
                
                elif choice == 2:
                    # Limit order
                    price = click.prompt("Limit Price")
                    from bot.validators import validate_price
                    validated_price = validate_price(price)
                    logger.info(f"Interactive limit order - {symbol} {side} {quantity} @ {price}")
                    response = manager.place_order(
                        symbol=symbol,
                        side=validated_side,
                        order_type=OrderType.LIMIT,
                        quantity=validated_qty,
                        price=validated_price
                    )
                
                elif choice == 3:
                    # Stop-limit order
                    price = click.prompt("Limit Price")
                    stop_price = click.prompt("Stop Price")
                    from bot.validators import validate_price
                    validated_price = validate_price(price)
                    validated_stop_price = validate_price(stop_price)
                    logger.info(
                        f"Interactive stop-limit order - {symbol} {side} {quantity} "
                        f"@ {price} stop {stop_price}"
                    )
                    response = manager.place_stop_limit_order(
                        symbol=symbol,
                        side=validated_side,
                        quantity=validated_qty,
                        price=validated_price,
                        stop_price=validated_stop_price
                    )
                
                click.echo(manager.format_order_response(response))
                click.secho(
                    f"✅ Order placed! ID: {response.get('orderId')}",
                    fg="green"
                )
            
            except (ValidationError, BinanceAPIError) as e:
                logger.error(f"Order failed: {str(e)}")
                click.secho(f"❌ Error: {str(e)}", fg="red")
        
        client.close()
    
    except click.ClickException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in interactive mode: {str(e)}")
        click.secho(f"❌ Error: {str(e)}", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    cli()
