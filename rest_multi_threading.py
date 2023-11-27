import threading
import ccxt
import os
import time
import logging
from datetime import datetime
import json
import atexit
import signal
import sys


# Create a semaphore with a limit of 5
semaphore = threading.Semaphore(2)
seq_id_counter = {}

seq_id_lock = threading.Lock()

SEQ_ID_FILE = "data/seq_id_counter.json"

def handler(signum, frame):
    save_seq_id_to_file()
    sys.exit(0)

def save_seq_id_to_file():
    with seq_id_lock, open(SEQ_ID_FILE, 'w') as file:
        json.dump(seq_id_counter, file)

def load_seq_id_from_file():
    global seq_id_counter
    if os.path.exists(SEQ_ID_FILE):
        with seq_id_lock, open(SEQ_ID_FILE, 'r') as file:
            seq_id_counter = json.load(file)
    else:
        seq_id_counter = {}

def fetch_symbol_data(exchange, symbol, exchange_id):
    global seq_id_counter
    # Acquire the semaphore
    semaphore.acquire()
    try:
        # Fetch Ticker Data
        ticker = exchange.fetch_ticker(symbol)
        collection_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        timestamp = datetime.utcfromtimestamp(ticker['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        filename = f"data/tick_{symbol.replace('/', '')}_{datetime.utcnow().strftime('%Y%m%d')}.txt"

        with open(filename, 'a') as file:
            # Fetch Order Book Data
            order_book = exchange.fetch_order_book(symbol)
            for bid in order_book['bids']:
                # Ensuring Thread safe
                with seq_id_lock:
                    seq_id_counter[symbol] = seq_id_counter.get(symbol, 0) + 1
                    current_seq_id = seq_id_counter[symbol]

                file.write(f"{collection_timestamp},{timestamp},{current_seq_id},D,{exchange_id},1,{bid[0]},{bid[1]}\n")
            for ask in order_book['asks']:
                # Ensuring Thread safe
                with seq_id_lock:
                    seq_id_counter[symbol] = seq_id_counter.get(symbol, 0) + 1
                    current_seq_id = seq_id_counter[symbol]

                file.write(f"{collection_timestamp},{timestamp},{current_seq_id},D,{exchange_id},2,{ask[0]},{ask[1]}\n")
                
    except Exception as e:
        logging.error(f"Error fetching data for {symbol} on {exchange_id}: {str(e)}")
    finally:
        # Release the semaphore
        semaphore.release()

def fetch_crypto_data(exchange_id,target_symbols=None):
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
    markets = exchange.load_markets()
    
    if target_symbols != None:
        symbol_markets = {}
        for symbol in target_symbols:
            try:
                symbol_markets[symbol] = markets[symbol]
            except Exception as e:
                logging.error(f"Error fetching symbol {symbol} from {exchange_id}: {str(e)}")
        markets = symbol_markets
    
    threads = []
    for symbol, market in markets.items():
        t = threading.Thread(target=fetch_symbol_data, args=(exchange, symbol, exchange_id))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

def main():
    all_exchanges = ['kraken']#,'kucoin']
    target_symbols = ['BTC/USD', 'XRP/USD', 'ADA/USD', 'SOL/USD', 'ETH/USD']

    while True:  
        for exchange_id in all_exchanges:
            try:
                fetch_crypto_data(exchange_id,target_symbols)
            except Exception as e:
                logging.error(f"Error fetching data from {exchange_id}: {str(e)}")
        
        logging.info("Data has been saved to respective files")
        # time.sleep(60)


atexit.register(save_seq_id_to_file)
signal.signal(signal.SIGTERM, handler)

if __name__ == "__main__":
    load_seq_id_from_file()
    main()
