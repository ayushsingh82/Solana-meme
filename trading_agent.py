#!/usr/bin/env python3
"""
🚀 Solana-Meme Trading Agent - Recall Hackathon
===============================================

Comprehensive trading agent that integrates all functionality:
- Meme token discovery and analysis
- Portfolio management with risk controls
- Stop-loss execution
- Real-time market monitoring
- Performance analytics
"""

import os
import json
import time
import math
import requests
import schedule
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Import our custom modules
from solana_meme_fetcher import SolanaMemeFetcher
from solana_meme_loss_tracker import SolanaMemeLossTracker
from advanced_portfolio_manager import (
    load_targets, fetch_prices, fetch_holdings, get_market_metrics,
    analyze_portfolio_performance, compute_orders_with_risk_management,
    RiskManager, DRIFT_THRESHOLDS, STOP_LOSS_CONFIG, execute_trade,
    TOKEN_MAP, DECIMALS, COINGECKO_IDS, ASSET_DRIFT_THRESHOLDS
)

load_dotenv()

# ------------------------------------------------------------
#  Configuration
# ------------------------------------------------------------
RECALL_KEY = os.getenv("RECALL_API_KEY")
COINGECKO_KEY = os.getenv("PRODUCTION_API_KEY") or os.getenv("SANDBOX_API_KEY")
SANDBOX_API = "https://api.sandbox.competitions.recall.network"

# Trading configuration
TRADING_MODE = os.getenv("TRADING_MODE", "aggressive")  # conservative, moderate, aggressive, passive
REBALANCE_FREQUENCY = os.getenv("REBALANCE_FREQUENCY", "4h")  # 1h, 4h, 8h, 24h
STOP_LOSS_ENABLED = os.getenv("STOP_LOSS_ENABLED", "true").lower() == "true"

# ------------------------------------------------------------
#  Trading Agent Class
# ------------------------------------------------------------
class SolanaMemeTradingAgent:
    """Main trading agent that integrates all functionality."""
    
    def __init__(self):
        self.fetcher = SolanaMemeFetcher()
        self.loss_tracker = SolanaMemeLossTracker()
        self.risk_manager = RiskManager()
        self.trade_count = 0
        self.total_value = 0
        self.last_rebalance = None
        
        print("🚀 Solana-Meme Trading Agent Initialized")
        print(f"   Trading Mode: {TRADING_MODE}")
        print(f"   Rebalance Frequency: {REBALANCE_FREQUENCY}")
        print(f"   Stop-Loss Enabled: {STOP_LOSS_ENABLED}")
        print()
    
    def discover_meme_tokens(self, limit: int = 20) -> List[Dict]:
        """Discover trending Solana meme tokens."""
        print("🔍 Discovering trending Solana meme tokens...")
        meme_coins = self.fetcher.get_solana_meme_coins(limit=limit)
        
        if meme_coins:
            print(f"✅ Found {len(meme_coins)} trending meme coins")
            return meme_coins
        else:
            print("❌ No meme coins found")
            return []
    
    def analyze_market_performance(self) -> Dict:
        """Analyze 24-hour market performance."""
        print("📊 Analyzing 24-hour market performance...")
        
        # Get specific coin performance
        specific_coins = self.loss_tracker.track_specific_coins()
        all_meme_coins = self.loss_tracker.get_solana_meme_coins(limit=50)
        
        # Combine and remove duplicates
        all_coins = specific_coins + all_meme_coins
        unique_coins = []
        seen_ids = set()
        for coin in all_coins:
            if coin['id'] not in seen_ids:
                unique_coins.append(coin)
                seen_ids.add(coin['id'])
        
        # Analyze performance
        losers = [coin for coin in unique_coins if coin['price_change_percentage_24h'] < 0]
        gainers = [coin for coin in unique_coins if coin['price_change_percentage_24h'] > 0]
        
        analysis = {
            'total_coins': len(unique_coins),
            'losers': len(losers),
            'gainers': len(gainers),
            'biggest_losers': sorted(losers, key=lambda x: x['price_change_percentage_24h'])[:5],
            'biggest_gainers': sorted(gainers, key=lambda x: x['price_change_percentage_24h'], reverse=True)[:5],
            'average_change': sum(coin['price_change_percentage_24h'] for coin in unique_coins) / len(unique_coins) if unique_coins else 0
        }
        
        print(f"📈 Market Analysis: {analysis['gainers']} gainers, {analysis['losers']} losers")
        print(f"📊 Average 24h Change: {analysis['average_change']:.2f}%")
        
        return analysis
    
    def get_portfolio_status(self) -> Dict:
        """Get current portfolio status and analysis."""
        try:
            targets = load_targets()
            prices = fetch_prices(list(targets.keys()))
            holdings = fetch_holdings()
            metrics = get_market_metrics(list(targets.keys()))
            
            # Calculate total portfolio value
            total_value = sum(holdings.get(s, 0) * prices[s] for s in targets)
            self.total_value = total_value
            
            # Analyze portfolio performance
            analyze_portfolio_performance(holdings, prices, targets, metrics)
            
            return {
                'targets': targets,
                'prices': prices,
                'holdings': holdings,
                'metrics': metrics,
                'total_value': total_value
            }
        except Exception as e:
            print(f"❌ Portfolio analysis failed: {e}")
            return {}
    
    def compute_trading_orders(self, portfolio_data: Dict) -> List[Dict]:
        """Compute trading orders based on portfolio analysis."""
        if not portfolio_data:
            return []
        
        targets = portfolio_data['targets']
        prices = portfolio_data['prices']
        holdings = portfolio_data['holdings']
        metrics = portfolio_data['metrics']
        
        print("🧮 Computing trading orders...")
        
        try:
            orders = compute_orders_with_risk_management(targets, prices, holdings, metrics)
            print(f"📋 Generated {len(orders)} trading orders")
            return orders
        except Exception as e:
            print(f"❌ Failed to compute orders: {e}")
            return []
    
    def execute_trades(self, orders: List[Dict]) -> List[Dict]:
        """Execute trading orders."""
        if not orders:
            print("✅ No trades to execute")
            return []
        
        print(f"⚡ Executing {len(orders)} trades...")
        executed_trades = []
        
        for i, order in enumerate(orders, 1):
            try:
                print(f"   {i}/{len(orders)}: {order['side'].upper()} {order['amount']:.6f} {order['symbol']}")
                
                # Execute trade through Recall API
                result = execute_trade(
                    order['symbol'],
                    order['side'],
                    order['amount'],
                    order.get('reason', 'Portfolio rebalancing')
                )
                
                # Log trade
                trade_log = {
                    'timestamp': datetime.now().isoformat(),
                    'order': order,
                    'result': result,
                    'status': 'success'
                }
                executed_trades.append(trade_log)
                
                print(f"      ✅ Success: {result.get('status', 'unknown')}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"      ❌ Failed: {e}")
                trade_log = {
                    'timestamp': datetime.now().isoformat(),
                    'order': order,
                    'error': str(e),
                    'status': 'failed'
                }
                executed_trades.append(trade_log)
        
        self.trade_count += len(executed_trades)
        return executed_trades
    
    def save_trade_log(self, trades: List[Dict]):
        """Save trade execution log."""
        if not trades:
            return
        
        log_file = f"trade_execution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(log_file, 'w') as f:
                json.dump(trades, f, indent=2)
            print(f"📝 Trade log saved to {log_file}")
        except Exception as e:
            print(f"❌ Failed to save trade log: {e}")
    
    def run_market_analysis(self):
        """Run comprehensive market analysis."""
        print("\n" + "="*60)
        print("📊 MARKET ANALYSIS")
        print("="*60)
        
        # Discover meme tokens
        meme_tokens = self.discover_meme_tokens(limit=15)
        
        # Analyze market performance
        market_analysis = self.analyze_market_performance()
        
        # Show top performers
        if market_analysis['biggest_gainers']:
            print("\n🚀 TOP 5 GAINERS (24h):")
            for i, coin in enumerate(market_analysis['biggest_gainers'], 1):
                print(f"   {i}. {coin['name']} ({coin['symbol']}): {coin['price_change_percentage_24h']:+.2f}%")
        
        if market_analysis['biggest_losers']:
            print("\n🔴 TOP 5 LOSERS (24h):")
            for i, coin in enumerate(market_analysis['biggest_losers'], 1):
                print(f"   {i}. {coin['name']} ({coin['symbol']}): {coin['price_change_percentage_24h']:+.2f}%")
        
        print("="*60)
        return market_analysis
    
    def run_portfolio_rebalance(self):
        """Run portfolio rebalancing."""
        print("\n" + "="*60)
        print("🔄 PORTFOLIO REBALANCING")
        print("="*60)
        
        # Get portfolio status
        portfolio_data = self.get_portfolio_status()
        if not portfolio_data:
            print("❌ Failed to get portfolio data")
            return
        
        # Compute trading orders
        orders = self.compute_trading_orders(portfolio_data)
        if not orders:
            print("✅ Portfolio already balanced")
            return
        
        # Execute trades
        executed_trades = self.execute_trades(orders)
        
        # Save trade log
        self.save_trade_log(executed_trades)
        
        # Update last rebalance time
        self.last_rebalance = datetime.now()
        
        print("="*60)
        return executed_trades
    
    def run_risk_assessment(self):
        """Run risk assessment and monitoring."""
        print("\n" + "="*60)
        print("🛡️  RISK ASSESSMENT")
        print("="*60)
        
        try:
            targets = load_targets()
            metrics = get_market_metrics(list(targets.keys()))
            
            high_risk_assets = []
            low_volume_assets = []
            
            for symbol, data in metrics.items():
                if symbol in targets:
                    # Check volatility risk
                    volatility_risk, risk_msg = self.risk_manager.check_volatility_risk(symbol, metrics)
                    if volatility_risk:
                        high_risk_assets.append((symbol, risk_msg))
                    
                    # Check volume
                    if data['volume_24h'] < 1000000:
                        low_volume_assets.append(symbol)
            
            if high_risk_assets:
                print("🔴 HIGH RISK ASSETS:")
                for symbol, msg in high_risk_assets:
                    print(f"   • {symbol}: {msg}")
            else:
                print("✅ No high-risk assets detected")
            
            if low_volume_assets:
                print(f"\n⚠️  LOW VOLUME ASSETS: {', '.join(low_volume_assets)}")
            
            print("="*60)
            
        except Exception as e:
            print(f"❌ Risk assessment failed: {e}")
    
    def run_full_cycle(self):
        """Run complete trading cycle."""
        print(f"\n🔄 TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 1. Market Analysis
        market_analysis = self.run_market_analysis()
        
        # 2. Risk Assessment
        self.run_risk_assessment()
        
        # 3. Portfolio Rebalancing
        trades = self.run_portfolio_rebalance()
        
        # 4. Summary
        print("\n📊 CYCLE SUMMARY:")
        print(f"   • Market Analysis: {market_analysis['total_coins']} coins analyzed")
        print(f"   • Trades Executed: {len(trades)}")
        print(f"   • Total Portfolio Value: ${self.total_value:,.2f}")
        print(f"   • Total Trades (Session): {self.trade_count}")
        
        print("="*80)
    
    def start_continuous_trading(self):
        """Start continuous trading with scheduled rebalancing."""
        print("🚀 Starting continuous trading mode...")
        print("Press Ctrl-C to stop")
        
        # Set up scheduling based on frequency
        if REBALANCE_FREQUENCY == "1h":
            schedule.every().hour.do(self.run_full_cycle)
        elif REBALANCE_FREQUENCY == "4h":
            schedule.every(4).hours.do(self.run_full_cycle)
        elif REBALANCE_FREQUENCY == "8h":
            schedule.every(8).hours.do(self.run_full_cycle)
        else:  # 24h
            schedule.every().day.at("09:00").do(self.run_full_cycle)
        
        # Run initial cycle
        self.run_full_cycle()
        
        # Continuous loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                print("\n👋 Trading agent stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in trading loop: {e}")
                time.sleep(60)

# ------------------------------------------------------------
#  Main Execution
# ------------------------------------------------------------
def main():
    """Main function to run the trading agent."""
    print("🚀 SOLANA-MEME TRADING AGENT")
    print("="*50)
    print("Recall Hackathon Project")
    print("Intelligent Solana Meme Token Trading")
    print("="*50)
    
    # Check API key
    if not RECALL_KEY:
        print("❌ RECALL_API_KEY not found in .env file")
        print("Please add your Recall API key to the .env file")
        return
    
    # Initialize agent
    agent = SolanaMemeTradingAgent()
    
    # Check command line arguments
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "discover":
            agent.discover_meme_tokens()
        elif command == "analyze":
            agent.analyze_market_performance()
        elif command == "portfolio":
            agent.get_portfolio_status()
        elif command == "risk":
            agent.run_risk_assessment()
        elif command == "rebalance":
            agent.run_portfolio_rebalance()
        elif command == "cycle":
            agent.run_full_cycle()
        elif command == "demo":
            # Run demo mode
            print("🎮 Running demo mode...")
            agent.run_market_analysis()
            agent.run_risk_assessment()
            print("\n✅ Demo completed")
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: discover, analyze, portfolio, risk, rebalance, cycle, demo")
    else:
        # Default: start continuous trading
        agent.start_continuous_trading()

if __name__ == "__main__":
    main()