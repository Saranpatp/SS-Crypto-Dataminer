import os
import json
import asyncio
import ccxt.pro
import logging
from datetime import datetime
import uuid
import atexit
import signal
import sys
from dotenv import load_dotenv
from enum import Enum
load_dotenv()

DATA_FOLDER_PATH = os.getenv('DATA_FOLDER_PATH', 'data/')
os.makedirs(DATA_FOLDER_PATH, exist_ok=True)

class TickType(Enum):
    TRADES = 'T'
    QOUTES = 'Q'
    ORDERBOOKBYORDER = 'D'
    ORDERBOOKBYPRICE = 'P'
    ORDERBOOKRESET = 'R'
    IMBALANCE = 'I'
    



orderbooks = {}
seq_id_counter = {}
seq_id_lock = asyncio.Lock()

SEQ_ID_FILE = f"{DATA_FOLDER_PATH}seq_id_counter.json"

def save_seq_id_to_file_sync():
    with open(SEQ_ID_FILE, 'w') as file:
        json.dump(seq_id_counter, file)


async def load_seq_id_from_file():
    global seq_id_counter
    if os.path.exists(SEQ_ID_FILE):
        with open(SEQ_ID_FILE, 'r') as file:
            seq_id_counter = json.load(file)
    else:
        seq_id_counter = {}


def generate_uint64():
    random_uuid = uuid.uuid4()
    int_val = random_uuid.int

    # Mask out everything but the least significant 64 bits
    uint64_val = int_val & ((1 << 64) - 1)
    return uint64_val

def handle_orderbook(orderbook, symbol, exchange_id):
    collection_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')#[:-3]
    timestamp = datetime.utcfromtimestamp(orderbook['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')#[:-3]
    filename = f"{DATA_FOLDER_PATH}tick_{symbol.replace('/', '')}_{datetime.utcnow().strftime('%Y%m%d')}.txt"
    
    with open(filename, 'a') as file:
        for bid in orderbook['bids']:
            current_seq_id = seq_id_counter.get(symbol, 0) + 1
            seq_id_counter[symbol] = current_seq_id
            file.write(f"{collection_timestamp},{timestamp},{current_seq_id},{TickType.ORDERBOOKBYPRICE.value},{exchange_id},1,{bid[0]},{bid[1]}\n")

        for ask in orderbook['asks']:
            current_seq_id = seq_id_counter.get(symbol, 0) + 1
            seq_id_counter[symbol] = current_seq_id
            file.write(f"{collection_timestamp},{timestamp},{current_seq_id},{TickType.ORDERBOOKBYPRICE.value},{exchange_id},2,{ask[0]},{ask[1]}\n")

async def handle_trade(trade, symbol, exchange_id):
    collection_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')#[:-3]
    timestamp = datetime.utcfromtimestamp(trade['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')#[:-3]
    filename = f"{DATA_FOLDER_PATH}tick_{symbol.replace('/', '')}_{datetime.utcnow().strftime('%Y%m%d')}.txt"
    
    with open(filename, 'a') as file:
        current_seq_id = seq_id_counter.get(symbol, 0) + 1
        seq_id_counter[symbol] = current_seq_id
        file.write(f"{collection_timestamp},{timestamp},{current_seq_id},{TickType.TRADES.value},{exchange_id},{trade['price']},{trade['amount']}\n")
        # print(f"{collection_timestamp},{timestamp},{current_seq_id},T,{exchange_id},{trade['price']},{trade['amount']}\n")

async def handle_ticker(ticker, symbol, exchange_id):
    collection_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    timestamp = datetime.utcfromtimestamp(ticker['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')
    filename = f"{DATA_FOLDER_PATH}tick_{symbol.replace('/', '')}_{datetime.utcnow().strftime('%Y%m%d')}.txt"

    with open(filename, 'a') as file:
        current_seq_id = seq_id_counter.get(symbol, 0) + 1
        seq_id_counter[symbol] = current_seq_id
        file.write(f"{collection_timestamp},{timestamp},{current_seq_id},{TickType.QOUTES.value},{exchange_id},{ticker['bid']},{ticker['ask']}\n")
        # print(f"{collection_timestamp},{timestamp},{current_seq_id},Q,{exchange_id},{ticker['bid']},{ticker['ask']}\n")

async def ticker_loop(exchange, symbol):
    while True:
        try:
            ticker = await exchange.watch_ticker(symbol)
            await handle_ticker(ticker, symbol, exchange.id)
        except Exception as e:
            logging.error(f"Error fetching ticker data for {symbol} on {exchange.id}: {str(e)}")
            break

async def trade_loop(exchange, symbol):
    while True:
        try:
            trades = await exchange.watch_trades(symbol)
            for trade in trades:
                await handle_trade(trade, symbol, exchange.id)
        except Exception as e:
            logging.error(f"Error fetching trade data for {symbol} on {exchange.id}: {str(e)}")
            break

async def orderbook_loop(exchange, symbol):
    while True:
        try:
            orderbook = await exchange.watch_order_book(symbol)
            handle_orderbook(orderbook, symbol, exchange.id)
        except Exception as e:
            logging.error(f"Error fetching orderbook for {symbol} on {exchange.id}: {str(e)}")
            break


async def exchange_loop(exchange_id, symbols):
    exchange = getattr(ccxt.pro, exchange_id)()
    orderbook_loops = [orderbook_loop(exchange, symbol) for symbol in symbols]
    trade_loops = [trade_loop(exchange, symbol) for symbol in symbols]
    ticker_loops = [ticker_loop(exchange, symbol) for symbol in symbols]
    await asyncio.gather(*(orderbook_loops + trade_loops + ticker_loops))
    # await asyncio.gather(*(orderbook_loops + trade_loops))
    await exchange.close()


async def main():
    target_symbols = ['BTC/USDT', 'ETH/BTC']
    all_exchanges = {
        'bitfinex': target_symbols,
        # 'gate': target_symbols, # Different type of symbol
        # 'bitstamp': target_symbols, # Not supported watch ticker
        'kucoin': target_symbols,
        'upbit': target_symbols,
        'kraken': target_symbols + ['BTC/USD', 'XRP/USD', 'ADA/USD', 'SOL/USD', 'ETH/USD'],
        'okex': target_symbols,
        # 'binanceus': target_symbols + ['BTC_USDT', 'XRP/USD', 'ADA/USD', 'SOL/USD', 'ETH/USD'], # Mostly not supported socket connection
    }

    await load_seq_id_from_file()

    loops = [exchange_loop(exchange_id, symbols) for exchange_id, symbols in all_exchanges.items()]
    await asyncio.gather(*loops)

    # await save_seq_id_to_file()

atexit.register(save_seq_id_to_file_sync)
signal.signal(signal.SIGTERM, lambda signum, frame: save_seq_id_to_file_sync())


if __name__ == "__main__":
    asyncio.run(main())
