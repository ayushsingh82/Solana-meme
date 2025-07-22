import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import pandas as pd

# Load environment variables
load_dotenv()

class SolanaMemeLossTracker:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = os.getenv('PRODUCTION_API_KEY') or os.getenv('SANDBOX_API_KEY')
        
        # Popular Solana meme coins to track
        self.target_coins = [
            'dogwifhat', 'bonk', 'book-of-meme', 'popcat', 'myro', 'catwifhat',
            'dogwifhat', 'bonk', 'book-of-meme', 'popcat', 'myro', 'catwifhat',
            'jupiter', 'raydium', 'orca', 'serum', 'samoyedcoin', 'solana',
            'pepe', 'wojak', 'floki', 'shiba-inu', 'doge', 'moon'
        ]
        
    def get_coin_data(self, coin_id):
        """
        Get current data for a specific coin
        """
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {}
            
            if self.api_key:
                params['x_cg_demo_api_key'] = self.api_key
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'id': data['id'],
                'name': data['name'],
                'symbol': data['symbol'].upper(),
                'current_price': data['market_data']['current_price']['usd'],
                'price_change_24h': data['market_data']['price_change_24h'],
                'price_change_percentage_24h': data['market_data']['price_change_percentage_24h'],
                'market_cap': data['market_data']['market_cap']['usd'],
                'market_cap_change_24h': data['market_data']['market_cap_change_24h'],
                'market_cap_change_percentage_24h': data['market_data']['market_cap_change_percentage_24h'],
                'total_volume': data['market_data']['total_volume']['usd'],
                'volume_change_24h': data['market_data']['total_volume']['usd_24h_change'],
                'circulating_supply': data['market_data']['circulating_supply'],
                'total_supply': data['market_data']['total_supply'],
                'max_supply': data['market_data']['max_supply'],
                'ath': data['market_data']['ath']['usd'],
                'ath_change_percentage': data['market_data']['ath_change_percentage']['usd'],
                'atl': data['market_data']['atl']['usd'],
                'atl_change_percentage': data['market_data']['atl_change_percentage']['usd'],
                'last_updated': data['last_updated']
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {coin_id}: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing data for {coin_id}: {e}")
            return None
    
    def get_solana_meme_coins(self, limit=100):
        """
        Get all Solana meme coins and filter for losses
        """
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False,
                'platform': 'solana'
            }
            
            if self.api_key:
                params['x_cg_demo_api_key'] = self.api_key
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            coins = response.json()
            
            # Filter for meme coins with losses
            meme_coins_with_losses = []
            for coin in coins:
                name_lower = coin['name'].lower()
                symbol_lower = coin['symbol'].lower()
                
                # Meme coin keywords
                meme_keywords = ['moon', 'doge', 'shib', 'inu', 'cat', 'dog', 'pepe', 'wojak', 
                               'meme', 'floki', 'elon', 'wif', 'bonk', 'book', 'pop', 'myro']
                
                is_meme = any(keyword in name_lower or keyword in symbol_lower for keyword in meme_keywords)
                has_loss = coin['price_change_percentage_24h'] < 0
                
                if is_meme and has_loss:
                    meme_coins_with_losses.append({
                        'id': coin['id'],
                        'name': coin['name'],
                        'symbol': coin['symbol'].upper(),
                        'current_price': coin['current_price'],
                        'price_change_24h': coin['price_change_24h'],
                        'price_change_percentage_24h': coin['price_change_percentage_24h'],
                        'market_cap': coin['market_cap'],
                        'market_cap_change_24h': coin['market_cap_change_24h'],
                        'market_cap_change_percentage_24h': coin['market_cap_change_percentage_24h'],
                        'total_volume': coin['total_volume'],
                        'circulating_supply': coin['circulating_supply'],
                        'last_updated': coin['last_updated']
                    })
            
            return meme_coins_with_losses
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Solana meme coins: {e}")
            return []
    
    def track_specific_coins(self):
        """
        Track specific popular Solana meme coins
        """
        print("Tracking specific Solana meme coins...")
        print("=" * 80)
        
        tracked_coins = []
        
        for coin_id in self.target_coins:
            print(f"Fetching data for {coin_id}...")
            coin_data = self.get_coin_data(coin_id)
            
            if coin_data:
                tracked_coins.append(coin_data)
                print(f"✓ {coin_data['name']} ({coin_data['symbol']}) - {coin_data['price_change_percentage_24h']:.2f}%")
            else:
                print(f"✗ Failed to fetch {coin_id}")
        
        return tracked_coins
    
    def analyze_losses(self, coins):
        """
        Analyze and categorize losses
        """
        if not coins:
            print("No coins to analyze.")
            return
        
        # Sort by percentage loss (worst first)
        coins_sorted = sorted(coins, key=lambda x: x['price_change_percentage_24h'])
        
        print("\n" + "=" * 100)
        print("SOLANA MEME COINS - 24 HOUR LOSS ANALYSIS")
        print("=" * 100)
        
        total_losses = 0
        total_gains = 0
        loss_count = 0
        gain_count = 0
        
        for i, coin in enumerate(coins_sorted, 1):
            change_pct = coin['price_change_percentage_24h']
            change_24h = coin['price_change_24h']
            
            if change_pct < 0:
                total_losses += abs(change_pct)
                loss_count += 1
                status = "📉 LOSS"
            else:
                total_gains += change_pct
                gain_count += 1
                status = "📈 GAIN"
            
            print(f"\n{i:2d}. {coin['name']} ({coin['symbol']}) {status}")
            print(f"    Current Price: ${coin['current_price']:,.8f}")
            print(f"    24h Change: ${change_24h:,.8f} ({change_pct:+.2f}%)")
            print(f"    Market Cap: ${coin['market_cap']:,.0f}")
            print(f"    Market Cap Change: {coin['market_cap_change_percentage_24h']:+.2f}%")
            print(f"    24h Volume: ${coin['total_volume']:,.0f}")
            print(f"    Circulating Supply: {coin['circulating_supply']:,.0f}")
        
        # Summary statistics
        print("\n" + "=" * 100)
        print("SUMMARY STATISTICS")
        print("=" * 100)
        print(f"Total Coins Analyzed: {len(coins_sorted)}")
        print(f"Coins with Losses: {loss_count}")
        print(f"Coins with Gains: {gain_count}")
        print(f"Average Loss: {total_losses/loss_count:.2f}%" if loss_count > 0 else "Average Loss: N/A")
        print(f"Average Gain: {total_gains/gain_count:.2f}%" if gain_count > 0 else "Average Gain: N/A")
        print(f"Net Market Sentiment: {(total_gains - total_losses):.2f}%")
        
        # Top 5 biggest losers
        losers = [coin for coin in coins_sorted if coin['price_change_percentage_24h'] < 0]
        if losers:
            print(f"\n🏆 TOP 5 BIGGEST LOSERS:")
            for i, coin in enumerate(losers[:5], 1):
                print(f"   {i}. {coin['name']} ({coin['symbol']}): {coin['price_change_percentage_24h']:.2f}%")
        
        # Top 5 biggest gainers
        gainers = [coin for coin in coins_sorted if coin['price_change_percentage_24h'] > 0]
        if gainers:
            print(f"\n🚀 TOP 5 BIGGEST GAINERS:")
            for i, coin in enumerate(gainers[:5], 1):
                print(f"   {i}. {coin['name']} ({coin['symbol']}): {coin['price_change_percentage_24h']:.2f}%")
    
    def save_to_csv(self, coins, filename=None):
        """
        Save data to CSV file
        """
        if not coins:
            print("No data to save.")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"solana_meme_losses_{timestamp}.csv"
        
        df = pd.DataFrame(coins)
        
        # Reorder columns for better readability
        columns_order = [
            'name', 'symbol', 'current_price', 'price_change_24h', 'price_change_percentage_24h',
            'market_cap', 'market_cap_change_24h', 'market_cap_change_percentage_24h',
            'total_volume', 'circulating_supply', 'last_updated'
        ]
        
        # Only include columns that exist in the data
        existing_columns = [col for col in columns_order if col in df.columns]
        df = df[existing_columns]
        
        df.to_csv(filename, index=False)
        print(f"\nData saved to {filename}")
    
    def save_to_json(self, coins, filename=None):
        """
        Save data to JSON file
        """
        if not coins:
            print("No data to save.")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"solana_meme_losses_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(coins, f, indent=2)
        
        print(f"Data also saved to {filename}")

def main():
    tracker = SolanaMemeLossTracker()
    
    print("🔍 SOLANA MEME COIN LOSS TRACKER")
    print("=" * 50)
    
    # Track specific popular coins
    print("\n1. Tracking specific popular Solana meme coins...")
    specific_coins = tracker.track_specific_coins()
    
    # Get all Solana meme coins with losses
    print("\n2. Fetching all Solana meme coins with losses...")
    all_meme_coins = tracker.get_solana_meme_coins(limit=100)
    
    # Combine and analyze
    all_coins = specific_coins + all_meme_coins
    
    # Remove duplicates based on coin ID
    unique_coins = []
    seen_ids = set()
    for coin in all_coins:
        if coin['id'] not in seen_ids:
            unique_coins.append(coin)
            seen_ids.add(coin['id'])
    
    if unique_coins:
        tracker.analyze_losses(unique_coins)
        tracker.save_to_csv(unique_coins)
        tracker.save_to_json(unique_coins)
    else:
        print("No meme coins found or all coins are showing gains.")

if __name__ == "__main__":
    main() 