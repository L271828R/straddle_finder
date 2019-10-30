import selenium
import sys
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from pymongo import MongoClient 
from conf import conf
from date_helper import get_nearest_workweek
import random
from page import OptionPage
from page import OptionTypes
from datetime import datetime

def get_straddles(driver ,ticker, conf):
    op = OptionPage(driver, conf)
    op.ticker = ticker
    arr = []
    isFirst = True
    if conf["limit_dates"] is not None and ticker not in conf['exceptions']:
        op.dates = op.get_available_months()[:conf["limit_dates"]]
    else:
        op.dates = op.get_available_months()[:conf['exception_limit']]

    for date in op.dates:
        if isFirst == False:
            op.goto(ticker, date)
        puts_itm = op.get_straddle(OptionTypes.IN_THE_MONEY_PUTS, date)
        calls_itm = op.get_straddle(OptionTypes.IN_THE_MONEY_CALLS, date)
        arr.append(puts_itm)
        arr.append(calls_itm)
        isFirst = False
    return arr

def driver_cleanup(driver):
    driver.close()
    driver.quit()


def isSaved(conn, ticker):
    db = conn.database 
    collection = db.straddles
    now = datetime.now().strftime("%Y-%m-%d")
    param = {
        'ticker': ticker,
        'time_stamp': now
    }
    cursor = collection.find(param)
    if cursor.count() > 0:
        # print("cursor returned true for {} {}".format(ticker, now))
        return True

    if cursor.count() == 0:
        nearest_weekday = get_nearest_workweek()
        param = {
            'ticker': ticker,
            'close_date': nearest_weekday
        }
        cursor = collection.find(param)
        if cursor.count() == 0:
            return False
        else:
            return True





def create_driver(conf):
    chrome_options = Options()  
    if conf["headless"]:
        chrome_options.add_argument("--headless")
    return  webdriver.Chrome(conf['chrome_driver_location'], chrome_options=chrome_options)
    

def save_straddle(conn, straddle):
    db = conn.database 
    collection = db.straddles
    if straddle is not None:
        cursor = collection.find({
            'strike':straddle['strike'],
            'date': straddle['date'],
            'type': straddle['type'],
            'ticker': straddle['ticker'],
            'close_date': straddle['close_date']
        })

        if cursor.count() == 0:
            collection.insert_one(straddle)
            return True
        else:
            return False

def get_vol(arr, days):
    for i, row in enumerate(arr):
        if row['type'] == 'put-in-the-money' and row['days_to_expiration'] == days:
            return row['be']
        elif row['type'] == 'put-in-the-money' and row['days_to_expiration'] < days \
             and arr[i+1]['days_to_expiration'] > days:

            if 'be' in row.keys() and 'be' in arr[i+1].keys():
                return calc_vol(row, arr[i+i],days) 
            else:
                return None

   


def calc_vol(v1, v2, target):
    y1 = float(v1['be'].strip("%"))
    x1 = float(v1['days_to_expiration'])

    y2 = float(v2['be'].strip("%"))
    x2 = float(v2['days_to_expiration'])

    m = (y1 - y2) / (x1 - x2)
    b = -1 * ( m * x1 - y1 )
    ans = (m * target) + b
    return str(round(ans,2)) + '%'
 
def get_straddle_by_ticker(conn, driver, conf, op, tick, i, total_count):
    if not isSaved(conn=conn, ticker=tick):
        print("{} of {}, currently {}".format(str(i), str(total_count), tick))
        op.goto(ticker=tick, date=None)
        time.sleep(1)
        # ticker_straddle = {'meta-data': [
            # '10-day-vol' : get_vol(arr, days=10),
            # '1-day-vol' : get_vol(arr, days=1)],
            # 'data': arr}
        try:
            arr = get_straddles(driver=driver, ticker=tick, conf=conf)
            save_count = 0
            for straddle in arr:
                if save_straddle(conn, straddle):
                    save_count += 1
            print("saved {} records".format(save_count))        
            print(datetime.now().strftime("%Y-%m-%d %H:%M"))
            op.dates = None
        except Exception as e:
            print("Unexpected error:", sys.exc_info()[0])
            print(e)



def main(conn):
    from tickers import tickers
    # tickers = ['mdb']
    print('Straddle Finder Selenium') 
    driver = create_driver(conf)
    if len(sys.argv) > 1:
        print("found it " + sys.argv[1])
        if sys.argv[1] == 'reverse': tickers.reverse()
        if sys.argv[1] == 'random': 
            random.shuffle(tickers)
    # tickers = ['spy']
    straddles = []
    op = OptionPage(driver=driver, conf=conf)
    for i, tick in enumerate(tickers):
        get_straddle_by_ticker(conn, driver, conf, op, tick, i, len(tickers))
    
    driver_cleanup(driver)
    print('Done')
    return straddles

if __name__ == '__main__':
    # CALCULATE BUSINESS DAYS
    conn = None
    try: 
       conn = MongoClient() 
       print("Connected successfully!!!") 
    except:   
       print("Could not connect to MongoDB") 
    main(conn=conn)




   
