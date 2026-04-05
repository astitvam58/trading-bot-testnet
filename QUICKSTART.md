# Quick Start Guide

## 5-Minute Setup

### Step 1: Install
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure
```bash
cp .env.example .env
# Edit .env with your Binance testnet API key and secret
```

### Step 3: Run
```bash
# Market order (interactive)
python cli.py market

# Limit order (interactive)
python cli.py limit

# Interactive menu
python cli.py interactive
```

## Command Examples

### Market Order - BUY
```bash
python cli.py market \
  --symbol BTCUSDT \
  --side BUY \
  --quantity 0.01
```

### Market Order - SELL
```bash
python cli.py market \
  --symbol ETHUSDT \
  --side SELL \
  --quantity 0.5
```

### Limit Order - BUY
```bash
python cli.py limit \
  --symbol BNBUSDT \
  --side BUY \
  --quantity 1 \
  --price 600.50
```

### Limit Order - SELL
```bash
python cli.py limit \
  --symbol BTCUSDT \
  --side SELL \
  --quantity 0.01 \
  --price 50000
```

### Stop-Limit Order
```bash
python cli.py stop_limit \
  --symbol BTCUSDT \
  --side BUY \
  --quantity 0.01 \
  --price 42000 \
  --stop-price 42100
```

## Check Logs
```bash
# View latest log file
tail -f logs/trading_bot_*.log

# View specific order type
cat logs/trading_bot_MARKET_example.log
cat logs/trading_bot_LIMIT_example.log
```

## Verify Setup
```bash
# Test API connection (requires valid credentials in .env)
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.01

# Should see successful order response or helpful error message
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `Missing Binance API credentials` | Check `.env` file exists with credentials |
| `Invalid API credentials` | Verify API key/secret in `.env` |
| `Symbol not found` | Use valid Binance symbols (BTCUSDT, ETHUSDT, etc.) |
| `Invalid quantity` | Use positive numbers (0.01, 1.5, etc.) |

## Next Steps

1. ✅ Complete setup above
2. ✅ Place a test market order
3. ✅ Place a test limit order
4. ✅ Check logs in `logs/` directory
5. ✅ Review code in `bot/` directory
6. ✅ Submit as per hiring instructions

---

Need help? Check the full README.md for detailed documentation.
