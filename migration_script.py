from pymongo import MongoClient
from tickers import tickers
from datetime import datetime as dt



conn = MongoClient()
now = dt.now()


def insert_ticker(conn, ticker):
    now = dt.now()
    record = {
        'ticker': ticker,
        'time_stamp': now}
    db = conn.database
    collection = db.tickers
    collection.insert_one(record)
    return True


def does_ticker_exit(conn, ticker):
    db = conn.database
    collection = db.tickers
    result = collection.find({'ticker':ticker})
    result = list(result)
    print('len=', len(result))
    if len(result) >0:
        return True
    if len(result) == 0:
        return False

def migrate():
    for ticker in tickers:
        insert_ticker(conn, ticker)

if __name__ == '__main__':
    import sys
    if sys.argv[1] == '--insert':
        ticker = sys.argv[2]
        if not does_ticker_exit(conn, ticker):
            ans = input(f"are you sure you want to insert {ticker}")
            if ans in ['y', 'yes']:
                insert_ticker(conn, ticker)
    else:
        print(f"ticker {ticker} already exists")




    # migrate()

