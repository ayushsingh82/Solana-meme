#!/usr/bin/env python3
"""
🚀 Solana-Meme Agent Setup Script
=================================

Quick setup script for the Recall hackathon project.
This script helps you configure and run the Solana-Meme agent.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("🚀 SOLANA-MEME AGENT SETUP")
    print("=" * 60)
    print("Recall Hackathon Project")
    print("Intelligent Solana Meme Token Trading Agent")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file with API keys."""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("🔧 Creating .env file...")
    
    env_content = """# Solana-Meme Agent Configuration
# Recall API (Required)
RECALL_API_KEY=your_recall_api_key_here

# CoinGecko API (Optional - for enhanced data)
PRODUCTION_API_KEY=c7ba1864dea0741e_9e32516fab7691f8
SANDBOX_API_KEY=110d6c1dd9a44b12_14d0dd729782cf29

# Trading Configuration
TRADING_MODE=aggressive  # conservative, moderate, aggressive, passive
REBALANCE_FREQUENCY=4h   # 1h, 4h, 8h, 24h
STOP_LOSS_ENABLED=true
"""
    
    try:
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please update RECALL_API_KEY with your actual API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_portfolio_config():
    """Create default portfolio configuration."""
    config_file = Path("advanced_portfolio_config.json")
    
    if config_file.exists():
        print("✅ Portfolio config already exists")
        return True
    
    print("📋 Creating default portfolio configuration...")
    
    config = {
        "WIF": 0.10,
        "BONK": 0.08,
        "BOME": 0.06,
        "POPCAT": 0.03,
        "MYRO": 0.03,
        "WETH": 0.15,
        "WBTC": 0.10,
        "USDC": 0.10,
        "LINK": 0.05,
        "UNI": 0.08,
        "AAVE": 0.06,
        "COMP": 0.06,
        "MATIC": 0.05,
        "AXS": 0.03,
        "SAND": 0.02
    }
    
    try:
        import json
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        print("✅ Portfolio configuration created")
        return True
    except Exception as e:
        print(f"❌ Failed to create portfolio config: {e}")
        return False

def run_demo():
    """Run the demo to test the setup."""
    print("🎮 Running demo to test setup...")
    try:
        subprocess.check_call([sys.executable, "demo_agent.py"])
        return True
    except subprocess.CalledProcessError:
        print("❌ Demo failed to run")
        return False
    except FileNotFoundError:
        print("⚠️  Demo script not found, skipping demo")
        return True

def show_next_steps():
    """Show next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. 🔑 Update your RECALL_API_KEY in the .env file")
    print("2. 🚀 Run the agent: python advanced_portfolio_manager.py")
    print("3. 🎮 Run the demo: python demo_agent.py")
    print("4. 📊 Monitor performance in the generated log files")
    print()
    print("Available Commands:")
    print("   • python advanced_portfolio_manager.py  # Main trading agent")
    print("   • python solana_meme_fetcher.py         # Meme token discovery")
    print("   • python solana_meme_loss_tracker.py    # Loss analysis")
    print("   • python demo_agent.py                  # Feature demo")
    print()
    print("📚 Documentation: README.md")
    print("🐛 Issues: Check the log files for errors")
    print()
    print("🚀 Ready to discover the next Solana meme moonshot!")
    print("=" * 60)

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return False
    
    print()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    print()
    
    # Create .env file
    if not create_env_file():
        return False
    
    print()
    
    # Create portfolio config
    if not create_portfolio_config():
        return False
    
    print()
    
    # Run demo (optional)
    demo_choice = input("🎮 Run demo to test setup? (y/n): ").lower().strip()
    if demo_choice in ['y', 'yes']:
        run_demo()
    
    print()
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1) 