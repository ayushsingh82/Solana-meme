import os, json, time, math, requests, schedule
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()                                     # read .env

# ------------------------------------------------------------
#  Configuration
# ------------------------------------------------------------
RECALL_KEY  = os.getenv("RECALL_API_KEY")
COINGECKO_KEY = os.getenv("PRODUCTION_API_KEY") or os.getenv("SANDBOX_API_KEY")
SANDBOX_API = "https://api.sandbox.competitions.recall.network"

# Solana meme coin addresses (you'll need to update these with actual addresses)
TOKEN_MAP = {
    "WIF": "0x...",      # Dogwifhat token address
    "BONK": "0x...",     # Bonk token address
    "BOME": "0x...",     # Book of Meme token address
    "POPCAT": "0x...",   # Popcat token address
    "MYRO": "0x...",     # Myro token address
    "CATWIF": "0x...",   # Catwifhat token address
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # 6 dec
}

DECIMALS = {
    "WIF": 6, "BONK": 5, "BOME": 6, "POPCAT": 6, "MYRO": 6, "CATWIF": 6,
    "USDC": 6
}

COINGECKO_IDS = {
    "WIF": "dogwifhat",
    "BONK": "bonk",
    "BOME": "book-of-meme",
    "POPCAT": "popcat",
    "MYRO": "myro",
    "CATWIF": "catwifhat",
    "USDC": "usd-coin",
}

DRIFT_THRESHOLD = 0.05    # rebalance if > 5% off target (higher for volatile meme coins)
REB_TIME        = "09:00" # local server time
MAX_SLIPPAGE    = 0.10    # 10% max slippage for meme coins

# ------------------------------------------------------------
#  Helper utilities
# ------------------------------------------------------------
def load_targets() -> dict[str, float]:
    """Load target portfolio weights from config file."""
    try:
        with open("meme_portfolio_config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        # Default meme coin portfolio weights
        default_targets = {
            "WIF": 0.25,      # 25% Dogwifhat
            "BONK": 0.20,     # 20% Bonk
            "BOME": 0.15,     # 15% Book of Meme
            "POPCAT": 0.15,   # 15% Popcat
            "MYRO": 0.15,     # 15% Myro
            "CATWIF": 0.10,   # 10% Catwifhat
        }
        save_targets(default_targets)
        return default_targets

def save_targets(targets: dict[str, float]):
    """Save target portfolio weights to config file."""
    with open("meme_portfolio_config.json", "w") as f:
        json.dump(targets, f, indent=2)

def to_base_units(amount_float: float, decimals: int) -> str:
    """Convert human units → integer string that Recall expects."""
    scaled = Decimal(str(amount_float)) * (10 ** decimals)
    return str(int(scaled.quantize(Decimal("1"), rounding=ROUND_DOWN)))

def log_trade(symbol: str, side: str, amount: float, price: float, status: str):
    """Log trade details to file."""
    trade_log = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "price": price,
        "status": status
    }
    
    try:
        with open("trade_log.json", "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []
    
    logs.append(trade_log)
    
    with open("trade_log.json", "w") as f:
        json.dump(logs, f, indent=2)

# ------------------------------------------------------------
#  Market data
# ------------------------------------------------------------
def fetch_prices(symbols: list[str]) -> dict[str, float]:
    """Fetch current prices from CoinGecko."""
    ids = ",".join(COINGECKO_IDS[sym] for sym in symbols if sym in COINGECKO_IDS)
    
    params = {"ids": ids, "vs_currencies": "usd"}
    if COINGECKO_KEY:
        params['x_cg_demo_api_key'] = COINGECKO_KEY
    
    r = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params=params,
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    
    prices = {}
    for sym in symbols:
        if sym in COINGECKO_IDS and COINGECKO_IDS[sym] in data:
            prices[sym] = data[COINGECKO_IDS[sym]]["usd"]
        else:
            print(f"⚠️  Warning: No price data for {sym}")
            prices[sym] = 0.0
    
    return prices

def fetch_holdings() -> dict[str, float]:
    """Return whole‑token balances from Recall's sandbox."""
    r = requests.get(
        f"{SANDBOX_API}/api/balance",
        headers={"Authorization": f"Bearer {RECALL_KEY}"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()

def get_meme_coin_metrics(symbols: list[str]) -> dict[str, dict]:
    """Get additional metrics for meme coins (volume, market cap, etc.)."""
    ids = ",".join(COINGECKO_IDS[sym] for sym in symbols if sym in COINGECKO_IDS)
    
    params = {
        "ids": ids,
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
    }
    
    if COINGECKO_KEY:
        params['x_cg_demo_api_key'] = COINGECKO_KEY
    
    r = requests.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params=params,
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    
    metrics = {}
    for coin in data:
        symbol = next((sym for sym, cg_id in COINGECKO_IDS.items() if cg_id == coin['id']), None)
        if symbol:
            metrics[symbol] = {
                "market_cap": coin['market_cap'],
                "volume_24h": coin['total_volume'],
                "price_change_24h": coin['price_change_percentage_24h'],
                "market_cap_rank": coin['market_cap_rank']
            }
    
    return metrics

# ------------------------------------------------------------
#  Trading logic
# ------------------------------------------------------------
def compute_orders(targets, prices, holdings):
    """Return a list of {'symbol','side','amount'} trades."""
    total_value = sum(holdings.get(s, 0) * prices[s] for s in targets)
    if total_value == 0:
        raise ValueError("No balances found; fund your sandbox wallet first.")

    overweight, underweight = [], []
    for sym, weight in targets.items():
        if sym not in prices or prices[sym] == 0:
            continue
            
        current_val = holdings.get(sym, 0) * prices[sym]
        target_val  = total_value * weight
        drift_pct   = (current_val - target_val) / total_value
        
        if abs(drift_pct) >= DRIFT_THRESHOLD:
            delta_val = abs(target_val - current_val)
            token_amt = delta_val / prices[sym]
            side      = "sell" if drift_pct > 0 else "buy"
            
            # Add slippage protection for meme coins
            if side == "buy":
                token_amt *= (1 + MAX_SLIPPAGE)  # Account for potential slippage
            
            (overweight if side == "sell" else underweight).append(
                {"symbol": sym, "side": side, "amount": token_amt}
            )

    # Execute sells first so we have USDC to fund buys
    return overweight + underweight

def execute_trade(symbol, side, amount_float):
    """Execute a trade through Recall API."""
    if symbol not in TOKEN_MAP:
        raise ValueError(f"Unknown token symbol: {symbol}")
    
    from_token, to_token = (
        (TOKEN_MAP[symbol], TOKEN_MAP["USDC"]) if side == "sell"
        else (TOKEN_MAP["USDC"], TOKEN_MAP[symbol])
    )

    payload = {
        "fromToken": from_token,
        "toToken":   to_token,
        "amount":    to_base_units(amount_float, DECIMALS[symbol]),
        "reason":    f"Automatic meme coin portfolio rebalance - {side} {symbol}",
    }
    
    r = requests.post(
        f"{SANDBOX_API}/api/trade/execute",
        json=payload,
        headers={
            "Authorization": f"Bearer {RECALL_KEY}",
            "Content-Type":  "application/json",
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json()

def analyze_portfolio_performance(holdings, prices, targets):
    """Analyze current portfolio performance."""
    total_value = sum(holdings.get(s, 0) * prices[s] for s in targets)
    
    print(f"\n{'='*60}")
    print(f"PORTFOLIO ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"Total Portfolio Value: ${total_value:,.2f}")
    print(f"\n{'Symbol':<8} {'Current %':<12} {'Target %':<12} {'Drift %':<12} {'Value':<15}")
    print("-" * 60)
    
    total_drift = 0
    for sym, target_weight in targets.items():
        if sym not in prices or prices[sym] == 0:
            continue
            
        current_val = holdings.get(sym, 0) * prices[sym]
        current_weight = current_val / total_value if total_value > 0 else 0
        drift_pct = (current_weight - target_weight) * 100
        
        print(f"{sym:<8} {current_weight*100:>8.2f}% {target_weight*100:>10.2f}% {drift_pct:>10.2f}% ${current_val:>12,.2f}")
        total_drift += abs(drift_pct)
    
    print(f"\nAverage Drift: {total_drift/len(targets):.2f}%")
    print(f"Rebalance Threshold: {DRIFT_THRESHOLD*100:.1f}%")

# ------------------------------------------------------------
#  Risk management
# ------------------------------------------------------------
def check_volatility_alerts(symbols: list[str]):
    """Check for high volatility in meme coins and issue alerts."""
    metrics = get_meme_coin_metrics(symbols)
    
    print(f"\n{'='*50}")
    print("VOLATILITY ALERTS")
    print(f"{'='*50}")
    
    for symbol, data in metrics.items():
        price_change = data['price_change_24h']
        
        if abs(price_change) > 20:
            alert = "🚨 HIGH VOLATILITY" if abs(price_change) > 50 else "⚠️  MODERATE VOLATILITY"
            print(f"{symbol}: {alert} - {price_change:+.2f}% (24h)")
        
        # Check volume
        if data['volume_24h'] < 1000000:  # Less than $1M volume
            print(f"{symbol}: ⚠️  LOW VOLUME - ${data['volume_24h']:,.0f} (24h)")

def adjust_targets_for_volatility(targets: dict[str, float], metrics: dict[str, dict]) -> dict[str, float]:
    """Adjust targets based on volatility and market conditions."""
    adjusted_targets = targets.copy()
    
    for symbol, data in metrics.items():
        if symbol in adjusted_targets:
            price_change = abs(data['price_change_24h'])
            
            # Reduce allocation for highly volatile coins
            if price_change > 50:
                adjusted_targets[symbol] *= 0.8  # Reduce by 20%
                print(f"Reducing {symbol} allocation due to high volatility ({price_change:.1f}%)")
            
            # Increase allocation for stable coins
            elif price_change < 10:
                adjusted_targets[symbol] *= 1.1  # Increase by 10%
                print(f"Increasing {symbol} allocation due to stability ({price_change:.1f}%)")
    
    # Normalize weights to sum to 1
    total_weight = sum(adjusted_targets.values())
    if total_weight > 0:
        adjusted_targets = {k: v/total_weight for k, v in adjusted_targets.items()}
    
    return adjusted_targets

# ------------------------------------------------------------
#  Daily job
# ------------------------------------------------------------
def rebalance():
    """Main rebalancing function."""
    print(f"\n🔄 Starting meme coin portfolio rebalance...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        targets = load_targets()
        prices = fetch_prices(list(targets.keys()))
        holdings = fetch_holdings()
        
        # Analyze current portfolio
        analyze_portfolio_performance(holdings, prices, targets)
        
        # Check volatility and adjust targets
        metrics = get_meme_coin_metrics(list(targets.keys()))
        check_volatility_alerts(list(targets.keys()))
        
        # Adjust targets based on market conditions
        adjusted_targets = adjust_targets_for_volatility(targets, metrics)
        if adjusted_targets != targets:
            print(f"\n📊 Adjusting targets based on market conditions...")
            save_targets(adjusted_targets)
            targets = adjusted_targets
        
        # Compute and execute orders
        orders = compute_orders(targets, prices, holdings)

        if not orders:
            print("✅ Portfolio already within ±5% of target.")
            return

        print(f"\n📈 Executing {len(orders)} trades...")
        for order in orders:
            try:
                res = execute_trade(**order)
                price = prices.get(order['symbol'], 0)
                log_trade(order['symbol'], order['side'], order['amount'], price, res.get('status', 'unknown'))
                print(f"✅ Executed {order['side']} {order['amount']:.6f} {order['symbol']} → {res.get('status', 'unknown')}")
            except Exception as e:
                print(f"❌ Failed to execute {order}: {e}")

        print("🎯 Meme coin portfolio rebalance complete.")
        
    except Exception as e:
        print(f"❌ Rebalancing failed: {e}")

# ------------------------------------------------------------
#  Scheduler
# ------------------------------------------------------------
schedule.every().day.at(REB_TIME).do(rebalance)

if __name__ == "__main__":
    print("🚀 Starting Solana Meme Coin Portfolio Manager...")
    print("Press Ctrl-C to quit")
    
    # Run initial rebalance
    rebalance()
    
    # Schedule daily rebalancing
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Portfolio manager stopped.")
            break 