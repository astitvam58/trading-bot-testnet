# Test Scenarios & Validation

This document outlines the test scenarios covered by the trading bot.

## Core Functionality Tests

### 1. Market Orders

#### 1.1 BUY Market Order
**Command:**
```bash
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.01
```

**Expected Behavior:**
- Order should be placed immediately
- Status should be "FILLED" or "PARTIALLY_FILLED"
- Average price should be populated
- Log should show successful placement

**Success Criteria:**
- ✅ Order ID returned
- ✅ Status is FILLED
- ✅ Executed quantity matches request
- ✅ Average price populated
- ✅ Entry logged with [INFO]

#### 1.2 SELL Market Order
**Command:**
```bash
python cli.py market --symbol ETHUSDT --side SELL --quantity 0.5
```

**Expected Behavior:**
- Same as BUY but for SELL side
- Should reduce position (if any)

#### 1.3 Various Symbols
Test with different trading pairs:
- BTCUSDT (Bitcoin)
- ETHUSDT (Ethereum)
- BNBUSDT (Binance Coin)
- SOLUSDT (Solana)

### 2. Limit Orders

#### 2.1 BUY Limit Order
**Command:**
```bash
python cli.py limit --symbol BTCUSDT --side BUY --quantity 0.01 --price 42000
```

**Expected Behavior:**
- Order should be placed but not immediately filled
- Status should be "NEW" or "PENDING_NEW"
- Price should match the specified price
- No average price until filled

**Success Criteria:**
- ✅ Order ID returned
- ✅ Status is NEW (not filled immediately)
- ✅ Price matches request
- ✅ Average price is empty (0)
- ✅ Entry logged with [INFO]

#### 2.2 SELL Limit Order
**Command:**
```bash
python cli.py limit --symbol ETHUSDT --side SELL --quantity 0.5 --price 2500
```

**Expected Behavior:**
- Same as BUY limit but for SELL

#### 2.3 Price Variations
Test with different price levels:
- Market price (should fill immediately)
- Below market (BUY) / Above market (SELL)
- Far below/above market (unlikely to fill)

### 3. Stop-Limit Orders (BONUS)

#### 3.1 BUY Stop-Limit
**Command:**
```bash
python cli.py stop_limit --symbol BTCUSDT --side BUY --quantity 0.01 --price 42000 --stop-price 42100
```

**Expected Behavior:**
- Order placed in PENDING_TRIGGER state
- When stop price (42100) is touched, converts to LIMIT order at price (42000)

#### 3.2 SELL Stop-Limit
**Command:**
```bash
python cli.py stop_limit --symbol ETHUSDT --side SELL --quantity 0.5 --price 2200 --stop-price 2100
```

## Input Validation Tests

### 1. Symbol Validation

#### 1.1 Empty Symbol
**Command:**
```bash
python cli.py market --symbol "" --side BUY --quantity 0.01
```
**Expected:** ❌ Validation Error - "Symbol cannot be empty"

#### 1.2 Invalid Characters
**Command:**
```bash
python cli.py market --symbol "BTC@USDT" --side BUY --quantity 0.01
```
**Expected:** ❌ Validation Error - "Invalid symbol"

#### 1.3 Too Short
**Command:**
```bash
python cli.py market --symbol "BT" --side BUY --quantity 0.01
```
**Expected:** ❌ Validation Error - "Symbol too short"

#### 1.4 Case Insensitivity
**Command:**
```bash
python cli.py market --symbol "btcusdt" --side BUY --quantity 0.01
```
**Expected:** ✅ Should normalize to "BTCUSDT"

### 2. Side Validation

#### 2.1 Invalid Side
**Command:**
```bash
python cli.py market --symbol BTCUSDT --side LONG --quantity 0.01
```
**Expected:** ❌ Validation Error - "Invalid side: LONG. Must be BUY or SELL."

#### 2.2 Valid Variations
**Commands:**
```bash
python cli.py market --symbol BTCUSDT --side buy --quantity 0.01   # lowercase
python cli.py market --symbol BTCUSDT --side Buy --quantity 0.01   # mixed case
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.01   # uppercase
```
**Expected:** ✅ All should work

### 3. Quantity Validation

#### 3.1 Negative Quantity
**Command:**
```bash
python cli.py market --symbol BTCUSDT --side BUY --quantity -0.01
```
**Expected:** ❌ Validation Error - "Quantity must be positive"

#### 3.2 Zero Quantity
**Command:**
```bash
python cli.py market --symbol BTCUSDT --side BUY --quantity 0
```
**Expected:** ❌ Validation Error - "Quantity must be positive"

#### 3.3 Non-Numeric
**Command:**
```bash
python cli.py market --symbol BTCUSDT --side BUY --quantity "abc"
```
**Expected:** ❌ Validation Error - "Must be a valid number"

#### 3.4 Valid Decimals
**Commands:**
```bash
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.01
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.001
python cli.py market --symbol BTCUSDT --side BUY --quantity 1.5
python cli.py market --symbol BTCUSDT --side BUY --quantity 100
```
**Expected:** ✅ All should work

### 4. Price Validation (LIMIT Orders)

#### 4.1 Missing Price for LIMIT
**Command:**
```bash
python cli.py limit --symbol BTCUSDT --side BUY --quantity 0.01
# When prompted for price, leave empty
```
**Expected:** ❌ Validation Error - "Price is required for LIMIT orders"

#### 4.2 Negative Price
**Command:**
```bash
python cli.py limit --symbol BTCUSDT --side BUY --quantity 0.01 --price -1000
```
**Expected:** ❌ Validation Error - "Price must be positive"

#### 4.3 Non-Numeric Price
**Command:**
```bash
python cli.py limit --symbol BTCUSDT --side BUY --quantity 0.01 --price "xyz"
```
**Expected:** ❌ Validation Error - "Must be a valid number"

#### 4.4 Valid Prices
**Commands:**
```bash
python cli.py limit --symbol BTCUSDT --side BUY --quantity 0.01 --price 42000
python cli.py limit --symbol BTCUSDT --side BUY --quantity 0.01 --price 42000.50
python cli.py limit --symbol BTCUSDT --side BUY --quantity 0.01 --price 0.0001
```
**Expected:** ✅ All should work

## API Error Tests

### 1. Invalid Credentials
**Setup:** Set invalid API key/secret in .env
**Command:**
```bash
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.01
```
**Expected:** ❌ API Error - "Unauthorized (401): Invalid API credentials"

### 2. Missing Credentials
**Setup:** Remove or empty .env
**Command:**
```bash
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.01
```
**Expected:** ❌ ClickException - "Missing Binance API credentials"

### 3. Rate Limiting
**Setup:** Make many requests rapidly
**Command:** Run multiple orders in rapid succession
**Expected:** ❌ API Error - "Rate limited (429): Too many requests"

### 4. Network Errors
**Setup:** Disconnect from internet or block binancefuture.com
**Command:**
```bash
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.01
```
**Expected:** ❌ API Error - "Connection error: Unable to connect"

### 5. Invalid Symbol (not on exchange)
**Command:**
```bash
python cli.py market --symbol INVALIDUSDT --side BUY --quantity 0.01
```
**Expected:** ❌ API Error - "Unknown symbol"

## Logging Tests

### 1. Log File Creation
**Expected:** Logs directory should contain `trading_bot_YYYYMMDD_HHMMSS.log` file

### 2. Market Order Logging
**File:** `logs/trading_bot_MARKET_example.log`
**Should contain:**
```
- Market order request with params
- Request DEBUG logs
- Response status and body
- Success info log
```

### 3. Limit Order Logging
**File:** `logs/trading_bot_LIMIT_example.log`
**Should contain:**
```
- Limit order request with price
- Request/response debug logs
- Success info log with order ID
```

### 4. Error Logging
**Scenario:** Place order with invalid price
**Should contain:**
```
- Error message [ERROR] level
- Full error details
- Stacktrace for exceptions
```

### 5. Log Format
**Expected format:**
```
YYYY-MM-DD HH:MM:SS - trading_bot - LEVEL - Message
2024-01-15 14:30:22 - trading_bot - INFO - Market order request...
```

## Performance Tests

### 1. Order Placement Speed
**Test:** Measure time from command to order confirmation
**Expected:** < 2 seconds for market orders

### 2. Multiple Rapid Orders
**Test:** Place 5 orders in succession
**Expected:** All should succeed without rate limit errors

### 3. Concurrent Requests (if supported)
**Note:** Current implementation is synchronous

## CLI UX Tests

### 1. Help Documentation
**Command:**
```bash
python cli.py --help
python cli.py market --help
python cli.py limit --help
python cli.py stop_limit --help
```
**Expected:** ✅ All should display clear help text

### 2. Interactive Mode
**Command:**
```bash
python cli.py interactive
```
**Expected:**
- ✅ Menu displays correctly
- ✅ Color output shows properly
- ✅ Can navigate through menu
- ✅ Can place orders
- ✅ Can exit gracefully

### 3. Error Messages
**Expected:** Clear, actionable error messages in red
```
❌ Validation Error: Invalid symbol
❌ API Error: Unauthorized (401)
```

### 4. Success Messages
**Expected:** Clear success messages in green
```
✅ Order placed! ID: 1234567890
```

## Bonus Features Tests

### 1. Stop-Limit Orders
**Command:**
```bash
python cli.py stop_limit --symbol BTCUSDT --side BUY --quantity 0.01 --price 42000 --stop-price 42100
```
**Expected:** ✅ Order placed with PENDING_TRIGGER status

### 2. Interactive Menu
**Command:**
```bash
python cli.py interactive
```
**Expected:** ✅ User-friendly menu with options

### 3. Enhanced CLI Output
**Expected:**
- Color-coded messages
- Formatted order response
- Clear sections
- Easy-to-read details

## Regression Tests

### 1. Existing Orders Still Work
After implementing new features, verify:
- [ ] Market orders still work
- [ ] Limit orders still work
- [ ] Validation still works
- [ ] Logging still works

### 2. Error Handling Still Works
- [ ] Invalid input rejected
- [ ] API errors handled gracefully
- [ ] Network errors handled gracefully
- [ ] Helpful error messages shown

## Test Results Template

```
Date: YYYY-MM-DD
Tester: [Name]
System: [Python version, OS]

Market Orders: ✅ / ⚠️ / ❌
Limit Orders: ✅ / ⚠️ / ❌
Stop-Limit Orders: ✅ / ⚠️ / ❌
Input Validation: ✅ / ⚠️ / ❌
API Errors: ✅ / ⚠️ / ❌
Logging: ✅ / ⚠️ / ❌
CLI UX: ✅ / ⚠️ / ❌
Help System: ✅ / ⚠️ / ❌

Notes:
[Any issues or observations]
```

---

## Checklist for Submission

- [ ] All core features tested
- [ ] All validation tests passed
- [ ] Error handling verified
- [ ] Logs created successfully
- [ ] README is comprehensive
- [ ] Code is clean and documented
- [ ] No hardcoded credentials
- [ ] .env.example provided
- [ ] Project structure is clean
- [ ] All dependencies in requirements.txt
