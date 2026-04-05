# Trading Bot - Binance Futures Testnet

A professional-grade Python trading bot for placing orders on Binance Futures Testnet (USDT-M). This application provides a clean, reusable structure with comprehensive logging, input validation, and error handling.

## Features

✅ **Core Features**
- Place **Market** orders (BUY/SELL)
- Place **Limit** orders (BUY/SELL)
- Clean CLI interface with Click
- Comprehensive input validation
- Structured logging to file
- Detailed error handling
- Network failure recovery

✨ **Bonus Features**
- Stop-Limit orders (3rd order type)
- Interactive CLI menu mode
- Enhanced user prompts with color output
- Production-ready code structure

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py           # Binance API client wrapper
│   ├── orders.py           # Order placement logic
│   ├── validators.py       # Input validation
│   └── logging_config.py   # Logging setup
├── cli.py                  # CLI entry point
├── requirements.txt        # Dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Setup

### 1. Prerequisites

- Python 3.8+
- pip or poetry

### 2. Install Dependencies

```bash
# Clone or download the project
cd trading_bot

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Binance Futures Testnet Account

1. **Register**: Go to https://testnet.binancefuture.com
2. **Verify**: Complete account verification
3. **Get Credentials**:
   - Navigate to Account Settings → API Management
   - Create a new API key
   - Enable "Futures Trading" permissions
   - Copy your API Key and Secret

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
# BINANCE_API_KEY=your_key_here
# BINANCE_API_SECRET=your_secret_here
```

**Important**: Never commit your `.env` file to version control. It's already in `.gitignore`.

### 5. Verify Setup

```bash
# Test that dependencies are installed
python -c "import click; import requests; print('Setup OK!')"
```

## Usage

All commands support both **prompt mode** (interactive) and **argument mode**.

### Market Order

Place a market order (executes immediately at best available price):

```bash
# Interactive mode
python cli.py market

# Command line arguments
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.01
```

**Example Output**:
```
Trading symbol (e.g., BTCUSDT): BTCUSDT
Order side (BUY/SELL): BUY
Order quantity: 0.01

============================================================
ORDER PLACED SUCCESSFULLY
============================================================
Order ID:           1234567890
Symbol:             BTCUSDT
Side:               BUY
Type:               MARKET
Status:             FILLED
Quantity:           0.01
Executed Qty:       0.01
Price:              
Average Price:      42500.50
============================================================
```

### Limit Order

Place a limit order (executes when price reaches target):

```bash
# Interactive mode
python cli.py limit

# Command line arguments
python cli.py limit --symbol BTCUSDT --side SELL --quantity 0.01 --price 43000
```

### Stop-Limit Order (Bonus)

Place a stop-limit order (combines stop and limit logic):

```bash
# Interactive mode
python cli.py stop_limit

# Command line arguments
python cli.py stop_limit --symbol BTCUSDT --side BUY --quantity 0.01 --price 42000 --stop-price 42100
```

### Interactive Menu (Bonus)

Launch an interactive menu for a better UX:

```bash
python cli.py interactive
```

This provides:
- Numbered menu selection
- Color-coded output
- Easy parameter input
- Error recovery within session

### Help

```bash
# General help
python cli.py --help

# Command-specific help
python cli.py market --help
python cli.py limit --help
python cli.py stop_limit --help
```

## Logging

Logs are automatically written to the `logs/` directory with timestamps.

### Log File Structure

```
logs/
└── trading_bot_20240115_143022.log
```

### Log Levels

- **DEBUG**: Detailed API calls and responses (file only)
- **INFO**: Order requests, successes, general flow (file + console)
- **ERROR**: API errors, validation failures (file + console)

### Example Log Output

```
2024-01-15 14:30:22 - trading_bot - INFO - Market order request - Symbol: BTCUSDT, Side: BUY, Quantity: 0.01
2024-01-15 14:30:22 - trading_bot - DEBUG - Request: POST /fapi/v1/order with params: {...}
2024-01-15 14:30:23 - trading_bot - DEBUG - Response status: 200
2024-01-15 14:30:23 - trading_bot - INFO - Market order placed successfully: {...}
```

## Error Handling

The bot handles the following error scenarios gracefully:

### Input Validation Errors
- Empty or invalid symbol
- Invalid side (not BUY/SELL)
- Invalid quantity (negative, non-numeric)
- Missing price for LIMIT orders
- Invalid price format

**Example**:
```
❌ Validation Error: Invalid side: LONG. Must be BUY or SELL.
```

### API Errors
- Invalid credentials
- Rate limiting (HTTP 429)
- Server errors (HTTP 500)
- Network timeouts
- Malformed JSON responses

**Example**:
```
❌ API Error: Unauthorized (401): Invalid API credentials
```

### Network Errors
- Connection failures
- DNS resolution errors
- Request timeouts

All errors are logged with full stack traces for debugging.

## Validation Rules

### Symbol
- Required, alphanumeric
- Minimum 3 characters
- Automatically converted to uppercase
- Examples: `BTCUSDT`, `ETHUSDT`, `BNBUSDT`

### Side
- Required: `BUY` or `SELL`
- Case-insensitive

### Order Type
- `MARKET`: Executes immediately
- `LIMIT`: Executes at specified price
- `STOP_LIMIT`: Executes when stop price is hit (bonus)

### Quantity
- Required, positive decimal number
- Examples: `0.01`, `1.5`, `10`

### Price (for LIMIT/STOP_LIMIT)
- Required for LIMIT and STOP_LIMIT orders
- Positive decimal number
- Examples: `42500.50`, `1000`, `0.5`

## API Reference

### Binance Client

The `BinanceClient` class wraps Binance Futures API:

```python
from bot.client import BinanceClient

client = BinanceClient(
    api_key="your_key",
    api_secret="your_secret",
    testnet=True  # Use testnet
)

# Place market order
response = client.place_market_order(
    symbol="BTCUSDT",
    side="BUY",
    quantity=0.01
)

# Place limit order
response = client.place_limit_order(
    symbol="BTCUSDT",
    side="SELL",
    quantity=0.01,
    price=43000
)

# Get order status
status = client.get_order_status(
    symbol="BTCUSDT",
    order_id=response['orderId']
)

client.close()
```

### Order Manager

The `OrderManager` class provides high-level order management:

```python
from bot.orders import OrderManager
from bot.validators import OrderSide, OrderType
from decimal import Decimal

manager = OrderManager(client)

response = manager.place_order(
    symbol="BTCUSDT",
    side=OrderSide.BUY,
    order_type=OrderType.MARKET,
    quantity=Decimal("0.01")
)

# Format for display
formatted = manager.format_order_response(response)
print(formatted)
```

## Testing Checklist

Before submitting, test the following scenarios:

- [ ] Market BUY order placed successfully
- [ ] Market SELL order placed successfully
- [ ] Limit BUY order placed successfully
- [ ] Limit SELL order placed successfully
- [ ] Invalid symbol validation
- [ ] Invalid quantity validation
- [ ] Missing price for LIMIT order
- [ ] API error handling (invalid credentials)
- [ ] Log files created with proper format
- [ ] Help text works (`--help` flags)

## Assumptions

1. **Testnet Only**: This bot is configured for Binance Futures Testnet by default
2. **USDT-M Futures**: All orders are placed on USDT-Margined futures
3. **GTC Time-in-Force**: Limit orders use "Good-Till-Cancelled" by default
4. **Decimal Precision**: Uses Python `Decimal` for accurate price/quantity handling
5. **HMAC-SHA256**: All signed requests use HMAC-SHA256 for authentication
6. **UTC Timestamps**: All timestamps are in UTC
7. **No Order Amendments**: The bot doesn't support order modifications
8. **Synchronous Execution**: All API calls are synchronous (blocking)

## Troubleshooting

### "Missing Binance API credentials"
**Solution**: Ensure `.env` file exists with `BINANCE_API_KEY` and `BINANCE_API_SECRET`

```bash
cp .env.example .env
# Edit .env with your credentials
```

### "Unauthorized (401): Invalid API credentials"
**Solution**: Verify that your API key and secret are correct and have "Futures Trading" permissions

### "Rate limited (429): Too many requests"
**Solution**: Wait before making more requests. The bot has built-in retry logic but respects rate limits

### "Connection error: Unable to connect to Binance"
**Solution**: Check your internet connection. Verify the testnet URL is accessible: https://testnet.binancefuture.com

### "Symbol not found"
**Solution**: Verify that the symbol exists on Binance Futures. Common symbols: BTCUSDT, ETHUSDT, BNBUSDT

## Performance & Production Considerations

This bot is suitable for:
- ✅ Educational purposes
- ✅ Small-scale trading
- ✅ Testing trading strategies on testnet
- ✅ Integration with larger systems

For production use, consider:
- Adding async/await for concurrent orders
- Implementing order book caching
- Adding risk management features
- Implementing circuit breakers
- Adding monitoring and alerting

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| python-binance | 1.0.17 | Binance API (optional) |
| requests | 2.31.0 | HTTP requests |
| click | 8.1.7 | CLI framework |
| python-dotenv | 1.0.0 | Environment variables |
| pydantic | 2.5.3 | Data validation |

## Security

⚠️ **Security Best Practices**:

1. **Never commit `.env` file**: It contains sensitive credentials
2. **Use environment variables**: Don't hardcode API keys
3. **Rotate credentials regularly**: Generate new API keys periodically
4. **Limit permissions**: Only enable "Futures Trading" permission
5. **Use testnet first**: Always test on testnet before mainnet
6. **Monitor logs**: Regularly review logs for suspicious activity

## Contributing

This is a hiring task submission. For improvements or bug reports, please reach out directly.

## License

This project is created as part of a hiring process for Sonika/Primetrade.ai

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review error logs in `logs/` directory
3. Verify setup steps were followed correctly

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0
