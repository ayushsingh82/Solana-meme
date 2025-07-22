import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class SolanaMemeFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = os.getenv('PRODUCTION_API_KEY') or os.getenv('SANDBOX_API_KEY')
        
    def get_solana_meme_coins(self, limit=50):
        """
        Fetch Solana meme coins from CoinGecko
        """
        try:
            # Search for Solana meme coins
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False,
                'platform': 'solana'  # Filter for Solana platform
            }
            
            if self.api_key:
                params['x_cg_demo_api_key'] = self.api_key
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            coins = response.json()
            
            # Filter for meme coins (you can customize this filter)
            meme_coins = []
            for coin in coins:
                # Check if it's likely a meme coin based on name/keywords
                name_lower = coin['name'].lower()
                symbol_lower = coin['symbol'].lower()
                
                meme_keywords = ['moon', 'doge', 'shib', 'inu', 'cat', 'dog', 'pepe', 'wojak', 'meme', 'floki', 'elon']
                is_meme = any(keyword in name_lower or keyword in symbol_lower for keyword in meme_keywords)
                
                if is_meme:
                    meme_coins.append({
                        'id': coin['id'],
                        'name': coin['name'],
                        'symbol': coin['symbol'].upper(),
                        'current_price': coin['current_price'],
                        'market_cap': coin['market_cap'],
                        'market_cap_rank': coin['market_cap_rank'],
                        'total_volume': coin['total_volume'],
                        'price_change_24h': coin['price_change_24h'],
                        'price_change_percentage_24h': coin['price_change_percentage_24h'],
                        'circulating_supply': coin['circulating_supply'],
                        'total_supply': coin['total_supply'],
                        'max_supply': coin['max_supply'],
                        'last_updated': coin['last_updated']
                    })
            
            return meme_coins
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return []
    
    def get_coin_details(self, coin_id):
        """
        Get detailed information about a specific coin
        """
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {}
            
            if self.api_key:
                params['x_cg_demo_api_key'] = self.api_key
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching coin details: {e}")
            return None
    
    def get_coin_price_history(self, coin_id, days=30):
        """
        Get price history for a specific coin
        """
        try:
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days
            }
            
            if self.api_key:
                params['x_cg_demo_api_key'] = self.api_key
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching price history: {e}")
            return None
    
    def save_to_json(self, data, filename=None):
        """
        Save data to a JSON file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"solana_meme_coins_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data saved to {filename}")
    
    def print_meme_coins(self, coins):
        """
        Print meme coins in a formatted way
        """
        print(f"\n{'='*80}")
        print(f"SOLANA MEME COINS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        for i, coin in enumerate(coins, 1):
            print(f"\n{i}. {coin['name']} ({coin['symbol']})")
            print(f"   Price: ${coin['current_price']:,.8f}")
            print(f"   Market Cap: ${coin['market_cap']:,.0f}")
            print(f"   Market Cap Rank: #{coin['market_cap_rank']}")
            print(f"   24h Change: {coin['price_change_percentage_24h']:.2f}%")
            print(f"   24h Volume: ${coin['total_volume']:,.0f}")
            print(f"   Circulating Supply: {coin['circulating_supply']:,.0f}")
            print(f"   Last Updated: {coin['last_updated']}")

def main():
    fetcher = SolanaMemeFetcher()
    
    print("Fetching Solana meme coins...")
    meme_coins = fetcher.get_solana_meme_coins(limit=20)
    
    if meme_coins:
        fetcher.print_meme_coins(meme_coins)
        fetcher.save_to_json(meme_coins)
        
        # Get detailed info for the first coin as an example
        if meme_coins:
            first_coin = meme_coins[0]
            print(f"\n{'='*80}")
            print(f"Detailed info for {first_coin['name']}:")
            print(f"{'='*80}")
            
            details = fetcher.get_coin_details(first_coin['id'])
            if details:
                print(f"Description: {details.get('description', {}).get('en', 'N/A')[:200]}...")
                print(f"Website: {details.get('links', {}).get('homepage', ['N/A'])[0] if details.get('links', {}).get('homepage') else 'N/A'}")
                print(f"Blockchain: {details.get('asset_platform_id', 'N/A')}")
                print(f"Genesis Date: {details.get('genesis_date', 'N/A')}")
    else:
        print("No meme coins found or error occurred.")

if __name__ == "__main__":
    main() 