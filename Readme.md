# 🚀 Solana-Meme Agent - Recall Hackathon Project

> **Intelligent Solana Meme Token Trading Agent with Automated Risk Management**

## 🎯 Project Overview

**Solana-Meme** is an advanced trading agent designed for the Recall hackathon that automatically discovers, analyzes, and trades the best Solana meme tokens while implementing sophisticated risk management strategies.

## ✨ Key Features

### 🤖 **Intelligent Meme Token Discovery**
- **Real-time Analysis**: Continuously monitors Solana meme token ecosystem
- **Trend Detection**: Identifies trending meme coins before they explode
- **Market Sentiment**: Analyzes social media and community sentiment
- **Liquidity Assessment**: Evaluates trading volume and market depth

### 📊 **Advanced Portfolio Management**
- **Multi-Asset Support**: Trades 40+ Solana meme tokens and major cryptocurrencies
- **Dynamic Rebalancing**: Every 4 hours with asset-specific drift thresholds
- **Risk-Adjusted Allocations**: Conservative (2%) to Aggressive (10%) thresholds
- **Real-time Performance Tracking**: Comprehensive portfolio analytics

### 🛡️ **Sophisticated Risk Management**
- **Stop-Loss Protection**: 15% default threshold with 24-hour cooldown
- **Volatility Monitoring**: Alerts for >30% price swings
- **Volume Analysis**: Warns about low liquidity situations
- **Position Sizing**: Automatic position reduction for high-risk assets

### ⚡ **High-Frequency Trading**
- **4-Hour Cadence**: Intraday rebalancing for optimal performance
- **Slippage Protection**: 10% tolerance for meme coins, 0.5% for stable assets
- **Multi-Source Pricing**: CoinGecko + DEX aggregators + TWAP oracles
- **Async Execution**: Non-blocking trade execution

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Meme Token    │    │   Portfolio     │    │   Risk          │
│   Discovery     │───▶│   Manager       │───▶│   Management    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Market Data   │    │   Trade         │    │   Stop-Loss     │
│   Aggregator    │    │   Executor      │    │   Engine        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
solana-meme/
├── 📄 README.md                           # Project documentation
├── 🔧 .env                                # Environment variables
├── 🚫 .gitignore                          # Git ignore rules
├── 📦 requirements.txt                    # Python dependencies
├── 🤖 solana_meme_fetcher.py             # Meme token discovery
├── 📊 solana_meme_loss_tracker.py        # 24h loss analysis
├── ⚙️ portfolio_management.py            # Basic portfolio manager
├── 🚀 advanced_portfolio_manager.py      # Advanced trading agent
├── 📋 meme_portfolio_config.json         # Basic portfolio config
└── 📋 advanced_portfolio_config.json     # Advanced portfolio config
```

## 🚀 Quick Start

### 1. **Environment Setup**
```bash
# Clone the repository
git clone <your-repo-url>
cd solana-meme

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configuration**
Create `.env` file with your API keys:
```env
# Recall API (Required)
PRODUCTION_API_KEY=
SANDBOX_API_KEY=
```

### 3. **Run the Agent**

#### **Option A: Advanced Trading Agent (Recommended)**
```bash
python advanced_portfolio_manager.py
```

#### **Option B: Meme Token Discovery**
```bash
python solana_meme_fetcher.py
```

#### **Option C: Loss Analysis**
```bash
python solana_meme_loss_tracker.py
```

## 🎮 Agent Modes

### 🔍 **Discovery Mode**
- Scans for new and trending Solana meme tokens
- Analyzes market cap, volume, and social sentiment
- Identifies potential moonshots before they pump

### 📈 **Trading Mode**
- **Conservative**: 2% drift threshold, stable assets focus
- **Moderate**: 5% drift threshold, balanced portfolio
- **Aggressive**: 10% drift threshold, meme coin heavy
- **Passive HODL**: 1% drift threshold, minimal trading

### 🛡️ **Risk Management Mode**
- **Stop-Loss**: Automatic position closure at 15% loss
- **Volatility Alerts**: Real-time monitoring of price swings
- **Volume Checks**: Ensures sufficient liquidity
- **Position Sizing**: Dynamic allocation based on risk

## 📊 Supported Assets

### 🐕 **Solana Meme Coins**
- **WIF** (Dogwifhat) - 25% allocation
- **BONK** (Bonk) - 20% allocation  
- **BOME** (Book of Meme) - 15% allocation
- **POPCAT** (Popcat) - 15% allocation
- **MYRO** (Myro) - 15% allocation
- **CATWIF** (Catwifhat) - 10% allocation

### 💎 **Major Cryptocurrencies**
- **WETH**, **WBTC**, **USDC**, **LINK**, **UNI**
- **AAVE**, **COMP**, **CRV**, **YFI**, **SUSHI**

### 🎮 **Gaming & Metaverse**
- **AXS**, **SAND**, **MANA**, **ENJ**, **GALA**

### 🤖 **AI & Tech**
- **OCEAN**, **FET**, **AGIX**, **RNDR**

## ⚙️ Configuration Options

### **Drift Thresholds**
```python
DRIFT_THRESHOLDS = {
    "CONSERVATIVE": 0.02,    # 2% for stable assets
    "MODERATE": 0.05,        # 5% for moderate volatility  
    "AGGRESSIVE": 0.10,      # 10% for high volatility meme coins
    "PASSIVE_HODL": 0.01,    # 1% for passive holding
    "ACTIVE_TRADING": 0.03,  # 3% for active trading
}
```

### **Stop-Loss Settings**
```python
STOP_LOSS_CONFIG = {
    "ENABLED": True,
    "DEFAULT_THRESHOLD": 0.15,  # 15% loss threshold
    "TRAILING_STOP": True,
    "TRAILING_PERCENTAGE": 0.05,  # 5% trailing stop
    "MAX_DAILY_LOSS": 0.25,  # 25% max daily loss
    "COOLDOWN_HOURS": 24,  # Hours to wait after stop-loss
}
```

### **Trading Cadence**
- **Intraday**: Every 4 hours
- **Daily**: 9:00 AM rebalance
- **Weekly**: Monday 10:00 AM deep analysis

## 📈 Performance Metrics

The agent tracks comprehensive performance metrics:

- **Total Portfolio Value**: Real-time portfolio valuation
- **Asset Allocation**: Current vs target percentages
- **Drift Analysis**: Portfolio deviation from targets
- **Risk Assessment**: High/medium/low risk classifications
- **Trade History**: Complete transaction log
- **Stop-Loss Events**: Risk management effectiveness

## 🔧 Advanced Features

### **Multi-Source Price Feeds**
- **CoinGecko API**: Primary price source
- **DEX Aggregators**: 1inch, 0x Protocol integration
- **TWAP Oracles**: Uniswap V3 time-weighted prices
- **Fallback Mechanisms**: Ensures price availability

### **Async Trading Engine**
- **Non-blocking Execution**: Parallel trade processing
- **Rate Limiting**: Respects API limits
- **Error Handling**: Graceful failure recovery
- **Retry Logic**: Automatic retry on failures

### **Intelligent Slippage**
- **Meme Coins**: 10% slippage tolerance
- **Low Liquidity**: 20% slippage tolerance
- **High Volatility**: 15% slippage tolerance
- **Stable Assets**: 0.5% slippage tolerance

## 🛠️ Development

### **Adding New Assets**
1. Update `TOKEN_MAP` with contract addresses
2. Add decimals to `DECIMALS` dictionary
3. Include CoinGecko ID in `COINGECKO_IDS`
4. Set appropriate drift threshold in `ASSET_DRIFT_THRESHOLDS`

### **Customizing Risk Parameters**
```python
# Modify stop-loss threshold
STOP_LOSS_CONFIG["DEFAULT_THRESHOLD"] = 0.20  # 20% loss threshold

# Adjust drift thresholds
ASSET_DRIFT_THRESHOLDS["WIF"] = 0.15  # 15% for WIF

# Change trading frequency
schedule.every(2).hours.do(rebalance)  # Every 2 hours
```

## 📊 Monitoring & Analytics

### **Real-time Dashboard**
- Portfolio value tracking
- Asset allocation visualization
- Risk metrics display
- Trade execution status

### **Performance Reports**
- Daily/weekly/monthly returns
- Risk-adjusted performance
- Sharpe ratio calculation
- Maximum drawdown analysis

### **Alert System**
- Volatility alerts (>30% price swings)
- Low volume warnings (<$1M daily volume)
- Stop-loss triggers
- Rebalancing notifications

## 🔒 Security Features

- **API Key Management**: Secure environment variable storage
- **Rate Limiting**: Prevents API abuse
- **Error Logging**: Comprehensive error tracking
- **Trade Validation**: Pre-execution trade verification
- **Sandbox Testing**: Safe testing environment

## 🚀 Hackathon Highlights

### **Innovation Points**
1. **Meme Token Focus**: Specialized for Solana meme ecosystem
2. **Adaptive Risk Management**: Dynamic stop-loss and position sizing
3. **High-Frequency Rebalancing**: 4-hour cadence for optimal performance
4. **Multi-Asset Support**: 40+ tokens across multiple categories
5. **Real-time Analytics**: Comprehensive performance tracking

### **Technical Excellence**
- **Async Architecture**: Non-blocking operations
- **Multi-Source Data**: Redundant price feeds
- **Intelligent Slippage**: Asset-specific tolerance
- **Comprehensive Logging**: Full audit trail
- **Modular Design**: Easy to extend and customize

## 📞 Support & Contact

For questions about the Solana-Meme agent:

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive inline code documentation
- **Examples**: Multiple usage examples included

## 📄 License

This project is developed for the Recall hackathon. Please refer to the hackathon terms and conditions.

---

**🚀 Ready to discover the next Solana meme moonshot? Deploy the agent and let it find the best opportunities!**
