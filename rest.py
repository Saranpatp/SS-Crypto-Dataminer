import ccxt
import os
import time
import logging
from datetime import datetime

# Setup logging
# logging.basicConfig(filename='crypto_data.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_crypto_data(exchange_id):
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
    markets = exchange.load_markets()
    
    for symbol, market in markets.items():
        try:
            # Fetch Ticker Data
            ticker = exchange.fetch_ticker(symbol)
            collection_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            timestamp = datetime.utcfromtimestamp(ticker['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            filename = f"data/tick_{symbol.replace('/', '')}_{datetime.utcnow().strftime('%Y%m%d')}.txt"

            with open(filename, 'a') as file:
                # Write Trades (Ticker Data)
                file.write(f"{collection_timestamp},{timestamp},{ticker['info'].get('id', 'NAN')},T,{exchange_id},{ticker['last']},{ticker['quoteVolume']},1\n")
                
                # Fetch Order Book Data
                order_book = exchange.fetch_order_book(symbol)
                for bid in order_book['bids']:
                    file.write(f"{collection_timestamp},{timestamp},{bid[0]},D,{exchange_id},1,{bid[0]},{bid[1]}\n")
                for ask in order_book['asks']:
                    file.write(f"{collection_timestamp},{timestamp},{ask[0]},D,{exchange_id},2,{ask[0]},{ask[1]}\n")
                
        except Exception as e:
            logging.error(f"Error fetching data for {symbol} on {exchange_id}: {str(e)}")

def main():
    all_exchanges = ['kraken']#,'kucoin']
    
    while True:  # Run indefinitely
        for exchange_id in all_exchanges:
            try:
                fetch_crypto_data(exchange_id)
            except Exception as e:
                logging.error(f"Error fetching data from {exchange_id}: {str(e)}")
        
        logging.info("Data has been saved to respective files")
        
        # Sleep for a specified interval (e.g., 3600 seconds or 1 hour) before the next iteration
        time.sleep(60)

if __name__ == "__main__":
    main()

