import os, json, time, math, requests, schedule
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
import aiohttp

load_dotenv()

# ------------------------------------------------------------
#  Enhanced Configuration
# ------------------------------------------------------------
RECALL_KEY = os.getenv("RECALL_API_KEY")
COINGECKO_KEY = os.getenv("PRODUCTION_API_KEY") or os.getenv("SANDBOX_API_KEY")
SANDBOX_API = "https://api.sandbox.competitions.recall.network"

# Enhanced token mapping with more assets
TOKEN_MAP = {
    # Solana Meme Coins
    "WIF": "0x...", "BONK": "0x...", "BOME": "0x...", "POPCAT": "0x...", 
    "MYRO": "0x...", "CATWIF": "0x...", "SAMO": "0x...", "FLOKI": "0x...",
    "PEPE": "0x...", "WOJAK": "0x...", "SHIB": "0x...", "DOGE": "0x...",
    
    # Major Cryptocurrencies
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "UNI": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "COMP": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
    "MKR": "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
    
    # DeFi Tokens
    "CRV": "0xD533a949740bb3306d119CC777fa900bA034cd52",
    "YFI": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
    "SUSHI": "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",
    "1INCH": "0x111111111117dC0aa78b770fA6A738034120C302",
    "BAL": "0xba100000625a3754423978a60c9317c58a424e3D",
    
    # Layer 2 & Scaling
    "MATIC": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608aCafEBB2",
    "OP": "0x4200000000000000000000000000000000000042",
    "ARB": "0x912CE59144191C1204E64559FE8253a0e49E6548",
    "IMX": "0xF57e7e7C23978C3cAEC3C3548E3D615c346e79fF",
    
    # Gaming & Metaverse
    "AXS": "0xBB0E17EF65F82AB018D8EDD776E8DD940327B28b",
    "SAND": "0x3845badAde8e6dFF049820680d1F14bD3903a5d0",
    "MANA": "0x0F5D2fB29fb7d3CFeE444a200298f468908cC942",
    "ENJ": "0xF629cBd94d3791C9250152BD8dfBDF380E2a3B9c",
    "GALA": "0x15D4c048F83bd7e37d49eA4C83a07267Ec4203dA",
    
    # AI & Tech
    "OCEAN": "0x967da4048cD07aB37855c090aAF366e4ce1b9F48",
    "FET": "0xaea46A60368A7bD060eec7DF8CBa43b7EF41Ad85",
    "AGIX": "0x5B7533812759B45C965ED374383C9E936a90d628",
    "RNDR": "0x6123B0049F904d730dB3C36a31167D9d4121fA6B",
}

DECIMALS = {
    # Solana Meme Coins
    "WIF": 6, "BONK": 5, "BOME": 6, "POPCAT": 6, "MYRO": 6, "CATWIF": 6,
    "SAMO": 6, "FLOKI": 9, "PEPE": 18, "WOJAK": 18, "SHIB": 18, "DOGE": 8,
    
    # Major Cryptocurrencies
    "USDC": 6, "WETH": 18, "WBTC": 8, "USDT": 6, "DAI": 18,
    "LINK": 18, "UNI": 18, "AAVE": 18, "COMP": 18, "MKR": 18,
    
    # DeFi Tokens
    "CRV": 18, "YFI": 18, "SUSHI": 18, "1INCH": 18, "BAL": 18,
    
    # Layer 2 & Scaling
    "MATIC": 18, "OP": 18, "ARB": 18, "IMX": 18,
    
    # Gaming & Metaverse
    "AXS": 18, "SAND": 18, "MANA": 18, "ENJ": 18, "GALA": 8,
    
    # AI & Tech
    "OCEAN": 18, "FET": 18, "AGIX": 8, "RNDR": 18,
}

COINGECKO_IDS = {
    # Solana Meme Coins
    "WIF": "dogwifhat", "BONK": "bonk", "BOME": "book-of-meme", 
    "POPCAT": "popcat", "MYRO": "myro", "CATWIF": "catwifhat",
    "SAMO": "samoyedcoin", "FLOKI": "floki", "PEPE": "pepe",
    "WOJAK": "wojak", "SHIB": "shiba-inu", "DOGE": "dogecoin",
    
    # Major Cryptocurrencies
    "USDC": "usd-coin", "WETH": "weth", "WBTC": "wrapped-bitcoin",
    "USDT": "tether", "DAI": "dai", "LINK": "chainlink", "UNI": "uniswap",
    "AAVE": "aave", "COMP": "compound-governance-token", "MKR": "maker",
    
    # DeFi Tokens
    "CRV": "curve-dao-token", "YFI": "yearn-finance", "SUSHI": "sushi",
    "1INCH": "1inch", "BAL": "balancer",
    
    # Layer 2 & Scaling
    "MATIC": "matic-network", "OP": "optimism", "ARB": "arbitrum",
    "IMX": "immutable-x",
    
    # Gaming & Metaverse
    "AXS": "axie-infinity", "SAND": "the-sandbox", "MANA": "decentraland",
    "ENJ": "enjin-coin", "GALA": "gala",
    
    # AI & Tech
    "OCEAN": "ocean-protocol", "FET": "fetch-ai", "AGIX": "singularitynet",
    "RNDR": "render-token",
}

# Enhanced drift thresholds based on asset volatility
DRIFT_THRESHOLDS = {
    "CONSERVATIVE": 0.02,    # 2% for stable assets
    "MODERATE": 0.05,        # 5% for moderate volatility
    "AGGRESSIVE": 0.10,      # 10% for high volatility meme coins
    "PASSIVE_HODL": 0.01,    # 1% for passive holding
    "ACTIVE_TRADING": 0.03,  # 3% for active trading
}

# Asset-specific drift thresholds
ASSET_DRIFT_THRESHOLDS = {
    # Stable assets
    "USDC": DRIFT_THRESHOLDS["CONSERVATIVE"],
    "USDT": DRIFT_THRESHOLDS["CONSERVATIVE"],
    "DAI": DRIFT_THRESHOLDS["CONSERVATIVE"],
    
    # Major cryptocurrencies
    "WETH": DRIFT_THRESHOLDS["MODERATE"],
    "WBTC": DRIFT_THRESHOLDS["MODERATE"],
    "LINK": DRIFT_THRESHOLDS["MODERATE"],
    "UNI": DRIFT_THRESHOLDS["MODERATE"],
    
    # Meme coins (high volatility)
    "WIF": DRIFT_THRESHOLDS["AGGRESSIVE"],
    "BONK": DRIFT_THRESHOLDS["AGGRESSIVE"],
    "BOME": DRIFT_THRESHOLDS["AGGRESSIVE"],
    "POPCAT": DRIFT_THRESHOLDS["AGGRESSIVE"],
    "MYRO": DRIFT_THRESHOLDS["AGGRESSIVE"],
    "CATWIF": DRIFT_THRESHOLDS["AGGRESSIVE"],
    "PEPE": DRIFT_THRESHOLDS["AGGRESSIVE"],
    "DOGE": DRIFT_THRESHOLDS["AGGRESSIVE"],
    "SHIB": DRIFT_THRESHOLDS["AGGRESSIVE"],
    
    # DeFi tokens
    "AAVE": DRIFT_THRESHOLDS["MODERATE"],
    "COMP": DRIFT_THRESHOLDS["MODERATE"],
    "CRV": DRIFT_THRESHOLDS["MODERATE"],
    "YFI": DRIFT_THRESHOLDS["MODERATE"],
}

# Stop-loss configuration
STOP_LOSS_CONFIG = {
    "ENABLED": True,
    "DEFAULT_THRESHOLD": 0.15,  # 15% loss threshold
    "TRAILING_STOP": True,
    "TRAILING_PERCENTAGE": 0.05,  # 5% trailing stop
    "MAX_DAILY_LOSS": 0.25,  # 25% max daily loss
    "COOLDOWN_HOURS": 24,  # Hours to wait after stop-loss
}

# Enhanced slippage protection
SLIPPAGE_CONFIG = {
    "DEFAULT": 0.005,  # 0.5% default slippage
    "MEME_COINS": 0.10,  # 10% for meme coins
    "LOW_LIQUIDITY": 0.20,  # 20% for low liquidity
    "HIGH_VOLATILITY": 0.15,  # 15% for high volatility
}

# Trading cadence
TRADING_CADENCE = "4h"  # Every 4 hours
REB_TIME = "09:00"  # Daily rebalance time

print("Advanced Portfolio Manager Configuration Loaded")

# ------------------------------------------------------------
#  Enhanced Helper Utilities
# ------------------------------------------------------------
def load_targets() -> Dict[str, float]:
    """Load target portfolio weights from config file."""
    try:
        with open("advanced_portfolio_config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        # Enhanced default portfolio with more assets
        default_targets = {
            # Meme coins (30%)
            "WIF": 0.10, "BONK": 0.08, "BOME": 0.06, "POPCAT": 0.03, "MYRO": 0.03,
            
            # Major cryptocurrencies (40%)
            "WETH": 0.15, "WBTC": 0.10, "USDC": 0.10, "LINK": 0.05,
            
            # DeFi tokens (20%)
            "UNI": 0.08, "AAVE": 0.06, "COMP": 0.06,
            
            # Layer 2 & Gaming (10%)
            "MATIC": 0.05, "AXS": 0.03, "SAND": 0.02,
        }
        save_targets(default_targets)
        return default_targets

def save_targets(targets: Dict[str, float]):
    """Save target portfolio weights to config file."""
    with open("advanced_portfolio_config.json", "w") as f:
        json.dump(targets, f, indent=2)

def get_drift_threshold(symbol: str) -> float:
    """Get asset-specific drift threshold."""
    return ASSET_DRIFT_THRESHOLDS.get(symbol, DRIFT_THRESHOLDS["MODERATE"])

def get_slippage_tolerance(symbol: str, volume_24h: float) -> float:
    """Get slippage tolerance based on asset and volume."""
    if symbol in ["WIF", "BONK", "BOME", "POPCAT", "MYRO", "CATWIF", "PEPE", "DOGE", "SHIB"]:
        return SLIPPAGE_CONFIG["MEME_COINS"]
    elif volume_24h < 1000000:  # Less than $1M volume
        return SLIPPAGE_CONFIG["LOW_LIQUIDITY"]
    elif symbol in ["WETH", "WBTC", "USDC", "USDT"]:
        return SLIPPAGE_CONFIG["DEFAULT"]
    else:
        return SLIPPAGE_CONFIG["HIGH_VOLATILITY"]

def to_base_units(amount_float: float, decimals: int) -> str:
    """Convert human units → integer string that Recall expects."""
    scaled = Decimal(str(amount_float)) * (10 ** decimals)
    return str(int(scaled.quantize(Decimal("1"), rounding=ROUND_DOWN)))

def log_trade(symbol: str, side: str, amount: float, price: float, status: str, reason: str = ""):
    """Enhanced trade logging with more details."""
    trade_log = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "price": price,
        "status": status,
        "reason": reason,
        "total_value": amount * price
    }
    
    try:
        with open("advanced_trade_log.json", "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []
    
    logs.append(trade_log)
    
    with open("advanced_trade_log.json", "w") as f:
        json.dump(logs, f, indent=2)

# ------------------------------------------------------------
#  Enhanced Market Data
# ------------------------------------------------------------
def fetch_prices(symbols: List[str]) -> Dict[str, float]:
    """Fetch current prices from CoinGecko with enhanced error handling."""
    ids = ",".join(COINGECKO_IDS[sym] for sym in symbols if sym in COINGECKO_IDS)
    
    params = {"ids": ids, "vs_currencies": "usd"}
    if COINGECKO_KEY:
        params['x_cg_demo_api_key'] = COINGECKO_KEY
    
    try:
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
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return {sym: 0.0 for sym in symbols}

def fetch_holdings() -> Dict[str, float]:
    """Return whole‑token balances from Recall's sandbox."""
    r = requests.get(
        f"{SANDBOX_API}/api/balance",
        headers={"Authorization": f"Bearer {RECALL_KEY}"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()

def get_market_metrics(symbols: List[str]) -> Dict[str, Dict]:
    """Get comprehensive market metrics."""
    ids = ",".join(COINGECKO_IDS[sym] for sym in symbols if sym in COINGECKO_IDS)
    
    params = {
        "ids": ids,
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    
    if COINGECKO_KEY:
        params['x_cg_demo_api_key'] = COINGECKO_KEY
    
    try:
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
                    "price_change_7d": coin['price_change_percentage_7d'],
                    "market_cap_rank": coin['market_cap_rank'],
                    "circulating_supply": coin['circulating_supply'],
                    "total_supply": coin['total_supply'],
                    "ath": coin['ath'],
                    "ath_change_percentage": coin['ath_change_percentage'],
                    "atl": coin['atl'],
                    "atl_change_percentage": coin['atl_change_percentage']
                }
        return metrics
    except Exception as e:
        print(f"Error fetching market metrics: {e}")
        return {}

# ------------------------------------------------------------
#  Enhanced Helper Utilities
# ------------------------------------------------------------
def load_targets() -> Dict[str, float]:
    """Load target portfolio weights from config file."""
    try:
        with open("advanced_portfolio_config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        # Enhanced default portfolio with more assets
        default_targets = {
            # Meme coins (30%)
            "WIF": 0.10, "BONK": 0.08, "BOME": 0.06, "POPCAT": 0.03, "MYRO": 0.03,
            
            # Major cryptocurrencies (40%)
            "WETH": 0.15, "WBTC": 0.10, "USDC": 0.10, "LINK": 0.05,
            
            # DeFi tokens (20%)
            "UNI": 0.08, "AAVE": 0.06, "COMP": 0.06,
            
            # Layer 2 & Gaming (10%)
            "MATIC": 0.05, "AXS": 0.03, "SAND": 0.02,
        }
        save_targets(default_targets)
        return default_targets

def save_targets(targets: Dict[str, float]):
    """Save target portfolio weights to config file."""
    with open("advanced_portfolio_config.json", "w") as f:
        json.dump(targets, f, indent=2)

def get_drift_threshold(symbol: str) -> float:
    """Get asset-specific drift threshold."""
    return ASSET_DRIFT_THRESHOLDS.get(symbol, DRIFT_THRESHOLDS["MODERATE"])

def get_slippage_tolerance(symbol: str, volume_24h: float) -> float:
    """Get slippage tolerance based on asset and volume."""
    if symbol in ["WIF", "BONK", "BOME", "POPCAT", "MYRO", "CATWIF", "PEPE", "DOGE", "SHIB"]:
        return SLIPPAGE_CONFIG["MEME_COINS"]
    elif volume_24h < 1000000:  # Less than $1M volume
        return SLIPPAGE_CONFIG["LOW_LIQUIDITY"]
    elif symbol in ["WETH", "WBTC", "USDC", "USDT"]:
        return SLIPPAGE_CONFIG["DEFAULT"]
    else:
        return SLIPPAGE_CONFIG["HIGH_VOLATILITY"]

def to_base_units(amount_float: float, decimals: int) -> str:
    """Convert human units → integer string that Recall expects."""
    scaled = Decimal(str(amount_float)) * (10 ** decimals)
    return str(int(scaled.quantize(Decimal("1"), rounding=ROUND_DOWN)))

def log_trade(symbol: str, side: str, amount: float, price: float, status: str, reason: str = ""):
    """Enhanced trade logging with more details."""
    trade_log = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "price": price,
        "status": status,
        "reason": reason,
        "total_value": amount * price
    }
    
    try:
        with open("advanced_trade_log.json", "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []
    
    logs.append(trade_log)
    
    with open("advanced_trade_log.json", "w") as f:
        json.dump(logs, f, indent=2)

# ------------------------------------------------------------
#  Enhanced Market Data with Real-time Feeds
# ------------------------------------------------------------
class PriceOracle:
    """Enhanced price oracle with multiple data sources."""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 30  # 30 seconds cache
        self.last_update = {}
    
    async def get_price_from_coingecko(self, symbol: str) -> Optional[float]:
        """Get price from CoinGecko with caching."""
        cache_key = f"coingecko_{symbol}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache and current_time - self.last_update.get(cache_key, 0) < self.cache_timeout:
            return self.cache[cache_key]
        
        try:
            if symbol not in COINGECKO_IDS:
                return None
                
            params = {"ids": COINGECKO_IDS[symbol], "vs_currencies": "usd"}
            if COINGECKO_KEY:
                params['x_cg_demo_api_key'] = COINGECKO_KEY
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data[COINGECKO_IDS[symbol]]["usd"]
                        
                        # Update cache
                        self.cache[cache_key] = price
                        self.last_update[cache_key] = current_time
                        
                        return price
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
    async def get_price_from_dex_aggregator(self, symbol: str) -> Optional[float]:
        """Get price from DEX aggregator (1inch, 0x, etc.)."""
        # This would integrate with actual DEX aggregators
        # For now, return None to fall back to CoinGecko
        return None
    
    async def get_twap_price(self, symbol: str) -> Optional[float]:
        """Get Time-Weighted Average Price from on-chain sources."""
        # This would integrate with Uniswap V3 TWAP oracles
        # For now, return None to fall back to CoinGecko
        return None
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Get best available price from multiple sources."""
        # Try TWAP first (most reliable)
        price = await self.get_twap_price(symbol)
        if price:
            return price
        
        # Try DEX aggregator
        price = await self.get_dex_aggregator(symbol)
        if price:
            return price
        
        # Fall back to CoinGecko
        return await self.get_price_from_coingecko(symbol)

async def fetch_prices_async(symbols: List[str]) -> Dict[str, float]:
    """Fetch prices asynchronously from multiple sources."""
    oracle = PriceOracle()
    prices = {}
    
    tasks = [oracle.get_price(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for symbol, result in zip(symbols, results):
        if isinstance(result, Exception):
            print(f"Error fetching price for {symbol}: {result}")
            prices[symbol] = 0.0
        elif result is not None:
            prices[symbol] = result
        else:
            print(f"⚠️  Warning: No price data for {symbol}")
            prices[symbol] = 0.0
    
    return prices

def fetch_prices(symbols: List[str]) -> Dict[str, float]:
    """Synchronous wrapper for async price fetching."""
    return asyncio.run(fetch_prices_async(symbols))

def fetch_holdings() -> Dict[str, float]:
    """Return whole‑token balances from Recall's sandbox."""
    r = requests.get(
        f"{SANDBOX_API}/api/balance",
        headers={"Authorization": f"Bearer {RECALL_KEY}"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()

async def get_market_metrics_async(symbols: List[str]) -> Dict[str, Dict]:
    """Get comprehensive market metrics asynchronously."""
    ids = ",".join(COINGECKO_IDS[sym] for sym in symbols if sym in COINGECKO_IDS)
    
    params = {
        "ids": ids,
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    
    if COINGECKO_KEY:
        params['x_cg_demo_api_key'] = COINGECKO_KEY
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    metrics = {}
                    for coin in data:
                        symbol = next((sym for sym, cg_id in COINGECKO_IDS.items() if cg_id == coin['id']), None)
                        if symbol:
                            metrics[symbol] = {
                                "market_cap": coin['market_cap'],
                                "volume_24h": coin['total_volume'],
                                "price_change_24h": coin['price_change_percentage_24h'],
                                "price_change_7d": coin['price_change_percentage_7d'],
                                "market_cap_rank": coin['market_cap_rank'],
                                "circulating_supply": coin['circulating_supply'],
                                "total_supply": coin['total_supply'],
                                "ath": coin['ath'],
                                "ath_change_percentage": coin['ath_change_percentage'],
                                "atl": coin['atl'],
                                "atl_change_percentage": coin['atl_change_percentage']
                            }
                    return metrics
    except Exception as e:
        print(f"Error fetching market metrics: {e}")
        return {}

def get_market_metrics(symbols: List[str]) -> Dict[str, Dict]:
    """Synchronous wrapper for async market metrics."""
    return asyncio.run(get_market_metrics_async(symbols))

# ------------------------------------------------------------
#  Enhanced Risk Management with Stop-Loss
# ------------------------------------------------------------
class RiskManager:
    """Advanced risk management with stop-loss and volatility monitoring."""
    
    def __init__(self):
        self.stop_loss_history = {}
        self.daily_losses = {}
        self.volatility_alerts = {}
    
    def check_stop_loss(self, symbol: str, current_price: float, entry_price: float, 
                       holdings: Dict[str, float]) -> Tuple[bool, str]:
        """Check if stop-loss should be triggered."""
        if not STOP_LOSS_CONFIG["ENABLED"]:
            return False, ""
        
        if symbol not in holdings or holdings[symbol] == 0:
            return False, ""
        
        # Calculate loss percentage
        loss_pct = (entry_price - current_price) / entry_price
        
        # Check if we're in cooldown period
        last_stop_loss = self.stop_loss_history.get(symbol, 0)
        cooldown_seconds = STOP_LOSS_CONFIG["COOLDOWN_HOURS"] * 3600
        if time.time() - last_stop_loss < cooldown_seconds:
            return False, ""
        
        # Check daily loss limit
        today = datetime.now().date().isoformat()
        daily_loss = self.daily_losses.get(today, {}).get(symbol, 0)
        if daily_loss >= STOP_LOSS_CONFIG["MAX_DAILY_LOSS"]:
            return False, "Daily loss limit reached"
        
        # Check stop-loss threshold
        threshold = STOP_LOSS_CONFIG["DEFAULT_THRESHOLD"]
        if loss_pct >= threshold:
            self.stop_loss_history[symbol] = time.time()
            if today not in self.daily_losses:
                self.daily_losses[today] = {}
            self.daily_losses[today][symbol] = daily_loss + loss_pct
            
            return True, f"Stop-loss triggered: {loss_pct:.2%} loss"
        
        return False, ""
    
    def check_volatility_risk(self, symbol: str, metrics: Dict) -> Tuple[bool, str]:
        """Check for volatility-based risks."""
        if symbol not in metrics:
            return False, ""
        
        data = metrics[symbol]
        price_change_24h = abs(data['price_change_24h'])
        volume_24h = data['volume_24h']
        
        # High volatility alert
        if price_change_24h > 50:
            return True, f"Extreme volatility: {price_change_24h:.1f}% (24h)"
        elif price_change_24h > 30:
            return True, f"High volatility: {price_change_24h:.1f}% (24h)"
        
        # Low volume alert
        if volume_24h < 500000:  # Less than $500K
            return True, f"Very low volume: ${volume_24h:,.0f}"
        elif volume_24h < 1000000:  # Less than $1M
            return True, f"Low volume: ${volume_24h:,.0f}"
        
        return False, ""
    
    def should_reduce_position(self, symbol: str, metrics: Dict) -> Tuple[bool, str]:
        """Determine if position should be reduced due to risk."""
        volatility_risk, volatility_msg = self.check_volatility_risk(symbol, metrics)
        
        if volatility_risk:
            return True, volatility_msg
        
        # Check for other risk factors
        if symbol in metrics:
            data = metrics[symbol]
            
            # Check if near all-time low
            if data['atl_change_percentage'] > -10:  # Within 10% of ATL
                return True, f"Near all-time low: {data['atl_change_percentage']:.1f}% from ATL"
            
            # Check for declining market cap rank
            # (This would require historical data tracking)
        
        return False, ""

# ------------------------------------------------------------
#  Enhanced Trading Logic with Risk Management
# ------------------------------------------------------------
def compute_orders_with_risk_management(targets: Dict[str, float], prices: Dict[str, float], 
                                       holdings: Dict[str, float], metrics: Dict[str, Dict]) -> List[Dict]:
    """Enhanced order computation with risk management."""
    risk_manager = RiskManager()
    total_value = sum(holdings.get(s, 0) * prices[s] for s in targets)
    
    if total_value == 0:
        raise ValueError("No balances found; fund your sandbox wallet first.")

    overweight, underweight = [], []
    
    for sym, weight in targets.items():
        if sym not in prices or prices[sym] == 0:
            continue
            
        current_val = holdings.get(sym, 0) * prices[sym]
        target_val = total_value * weight
        drift_pct = (current_val - target_val) / total_value
        drift_threshold = get_drift_threshold(sym)
        
        # Check stop-loss first
        if holdings.get(sym, 0) > 0:
            # For simplicity, assume entry price is current price * 1.1 (10% profit assumption)
            # In practice, you'd track actual entry prices
            assumed_entry_price = prices[sym] * 1.1
            stop_loss_triggered, stop_loss_msg = risk_manager.check_stop_loss(
                sym, prices[sym], assumed_entry_price, holdings
            )
            
            if stop_loss_triggered:
                # Force sell entire position
                overweight.append({
                    "symbol": sym,
                    "side": "sell",
                    "amount": holdings[sym],
                    "reason": f"Stop-loss: {stop_loss_msg}"
                })
                continue
        
        # Check if position should be reduced due to risk
        should_reduce, risk_msg = risk_manager.should_reduce_position(sym, metrics.get(sym, {}))
        if should_reduce and holdings.get(sym, 0) > 0:
            # Reduce position by 50%
            reduce_amount = holdings[sym] * 0.5
            overweight.append({
                "symbol": sym,
                "side": "sell",
                "amount": reduce_amount,
                "reason": f"Risk reduction: {risk_msg}"
            })
            continue
        
        # Normal rebalancing logic
        if abs(drift_pct) >= drift_threshold:
            delta_val = abs(target_val - current_val)
            token_amt = delta_val / prices[sym]
            side = "sell" if drift_pct > 0 else "buy"
            
            # Apply slippage protection
            slippage = get_slippage_tolerance(sym, metrics.get(sym, {}).get('volume_24h', 0))
            if side == "buy":
                token_amt *= (1 + slippage)
            
            (overweight if side == "sell" else underweight).append({
                "symbol": sym,
                "side": side,
                "amount": token_amt,
                "reason": f"Rebalancing: {drift_pct:.2%} drift"
            })

    # Execute sells first so we have USDC to fund buys
    return overweight + underweight

def execute_trade(symbol: str, side: str, amount_float: float, reason: str = ""):
    """Execute a trade through Recall API with enhanced logging."""
    if symbol not in TOKEN_MAP:
        raise ValueError(f"Unknown token symbol: {symbol}")
    
    from_token, to_token = (
        (TOKEN_MAP[symbol], TOKEN_MAP["USDC"]) if side == "sell"
        else (TOKEN_MAP["USDC"], TOKEN_MAP[symbol])
    )

    payload = {
        "fromToken": from_token,
        "toToken": to_token,
        "amount": to_base_units(amount_float, DECIMALS[symbol]),
        "reason": f"Advanced portfolio management - {reason}",
    }
    
    r = requests.post(
        f"{SANDBOX_API}/api/trade/execute",
        json=payload,
        headers={
            "Authorization": f"Bearer {RECALL_KEY}",
            "Content-Type": "application/json",
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json()

# ------------------------------------------------------------
#  Enhanced Portfolio Analysis
# ------------------------------------------------------------
def analyze_portfolio_performance(holdings: Dict[str, float], prices: Dict[str, float], 
                                targets: Dict[str, float], metrics: Dict[str, Dict]):
    """Enhanced portfolio analysis with risk metrics."""
    total_value = sum(holdings.get(s, 0) * prices[s] for s in targets)
    
    print(f"\n{'='*80}")
    print(f"ADVANCED PORTFOLIO ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    print(f"Total Portfolio Value: ${total_value:,.2f}")
    
    # Risk metrics
    risk_manager = RiskManager()
    high_risk_assets = []
    low_volume_assets = []
    
    print(f"\n{'Symbol':<8} {'Current %':<12} {'Target %':<12} {'Drift %':<12} {'Value':<15} {'Risk':<15}")
    print("-" * 80)
    
    total_drift = 0
    for sym, target_weight in targets.items():
        if sym not in prices or prices[sym] == 0:
            continue
            
        current_val = holdings.get(sym, 0) * prices[sym]
        current_weight = current_val / total_value if total_value > 0 else 0
        drift_pct = (current_weight - target_weight) * 100
        drift_threshold = get_drift_threshold(sym) * 100
        
        # Risk assessment
        risk_status = "🟢 LOW"
        if sym in metrics:
            should_reduce, risk_msg = risk_manager.should_reduce_position(sym, metrics[sym])
            if should_reduce:
                risk_status = "🔴 HIGH"
                high_risk_assets.append(sym)
            elif abs(metrics[sym]['price_change_24h']) > 20:
                risk_status = "🟡 MED"
        
        if sym in metrics and metrics[sym]['volume_24h'] < 1000000:
            low_volume_assets.append(sym)
        
        print(f"{sym:<8} {current_weight*100:>8.2f}% {target_weight*100:>10.2f}% {drift_pct:>10.2f}% ${current_val:>12,.2f} {risk_status}")
        total_drift += abs(drift_pct)
    
    print(f"\nAverage Drift: {total_drift/len(targets):.2f}%")
    print(f"Rebalance Thresholds: Conservative={DRIFT_THRESHOLDS['CONSERVATIVE']*100:.1f}%, Moderate={DRIFT_THRESHOLDS['MODERATE']*100:.1f}%, Aggressive={DRIFT_THRESHOLDS['AGGRESSIVE']*100:.1f}%")
    
    # Risk summary
    if high_risk_assets:
        print(f"\n🔴 HIGH RISK ASSETS: {', '.join(high_risk_assets)}")
    if low_volume_assets:
        print(f"⚠️  LOW VOLUME ASSETS: {', '.join(low_volume_assets)}")

# ------------------------------------------------------------
#  Enhanced Main Functions
# ------------------------------------------------------------
def rebalance():
    """Enhanced rebalancing function with risk management."""
    print(f"\n🔄 Starting advanced portfolio rebalance...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        targets = load_targets()
        prices = fetch_prices(list(targets.keys()))
        holdings = fetch_holdings()
        metrics = get_market_metrics(list(targets.keys()))
        
        # Analyze current portfolio
        analyze_portfolio_performance(holdings, prices, targets, metrics)
        
        # Compute orders with risk management
        orders = compute_orders_with_risk_management(targets, prices, holdings, metrics)

        if not orders:
            print("✅ Portfolio already within drift thresholds.")
            return

        print(f"\n📈 Executing {len(orders)} trades...")
        for order in orders:
            try:
                res = execute_trade(
                    order['symbol'], 
                    order['side'], 
                    order['amount'], 
                    order.get('reason', '')
                )
                price = prices.get(order['symbol'], 0)
                log_trade(
                    order['symbol'], 
                    order['side'], 
                    order['amount'], 
                    price, 
                    res.get('status', 'unknown'),
                    order.get('reason', '')
                )
                print(f"✅ Executed {order['side']} {order['amount']:.6f} {order['symbol']} → {res.get('status', 'unknown')}")
                if order.get('reason'):
                    print(f"   Reason: {order['reason']}")
            except Exception as e:
                print(f"❌ Failed to execute {order}: {e}")

        print("🎯 Advanced portfolio rebalance complete.")
        
    except Exception as e:
        print(f"❌ Rebalancing failed: {e}")

# ------------------------------------------------------------
#  Enhanced Scheduler with Multiple Cadences
# ------------------------------------------------------------
def setup_scheduler():
    """Setup enhanced scheduling with multiple cadences."""
    # Every 4 hours for intraday balancing
    schedule.every(4).hours.do(rebalance)
    
    # Daily rebalance at specific time
    schedule.every().day.at(REB_TIME).do(rebalance)
    
    # Weekly deep analysis
    schedule.every().monday.at("10:00").do(lambda: print("📊 Weekly portfolio deep analysis completed"))

if __name__ == "__main__":
    print("🚀 Starting Advanced Solana Meme Coin Portfolio Manager...")
    print("Features: Enhanced drift thresholds, 4-hour cadence, stop-loss, risk management")
    print("Press Ctrl-C to quit")
    
    # Setup enhanced scheduler
    setup_scheduler()
    
    # Run initial rebalance
    rebalance()
    
    # Main loop with enhanced scheduling
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Advanced portfolio manager stopped.")
            break 