import selenium
import sys
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from datetime import datetime
from pymongo import MongoClient 
from tickers import tickers
from conf import conf
from date_helper import get_nearest_workweek


class OptionTypes:
    IN_THE_MONEY_PUTS = "put-in-the-money"
    IN_THE_MONEY_CALLS = "call-in-the-money"

class OptionPage:
    def __init__(self, driver, conf):
        self.driver = driver
        self.STRIKE_COLUMN = 5 
        self.PUT_PRICE_COLUMN = 0 
        self.CALL_PRICE_COLUMN = 6
        self.ticker = None
        self.conf = conf
        self.once = False
        self.dates = None
    
    def goto(self, ticker, date=None):
        url = 'https://finance.yahoo.com/quote/__TICKER__/options?p=__TICKER__&straddle=true'
        url = url.replace('__TICKER__', ticker)
        self.driver.get(url)
        self.driver.implicitly_wait(8)
        self.once = True

        if date is not None:
            time.sleep(8)
            el_sel = Select(self.driver.find_element_by_tag_name("select"))
            el_sel.select_by_visible_text(date.strftime("%B %-d, %Y"))
        time.sleep(3)
        if self.conf['random_time'] == True:
            self.driver.implicitly_wait(random.randrange(5, 15))
        else:
            self.driver.implicitly_wait(3)
        self.driver.implicitly_wait(3)
        self.ticker = ticker

    def get_available_months(self):
        self.driver.implicitly_wait(8)
        el_sel = Select(self.driver.find_element_by_tag_name("select"))
        options = el_sel.options
        dates = []
        for op in options:
            dates.append(datetime.strptime(op.text, "%B %d, %Y"))
        return dates

    def get_close_date(self):
        close_date = None
        close_date_raw = self.driver.find_element_by_id("quote-market-notice").text
        if "At close" in close_date_raw:
            close_date = close_date_raw.split("At close: ")[1]
            close_date = close_date.replace(" EDT", "")
            close_dt = datetime.strptime(close_date, "%B %d %I:%M%p")
            close_date = close_dt.strftime( str(datetime.now().year) + "-%m-%d")
        return close_date



    def get_straddle(self, straddle_type, date):
        el_table = self.driver.find_element_by_css_selector("table.straddles")
        rows = el_table.find_elements_by_css_selector("tr." + straddle_type)
        if (straddle_type == OptionTypes.IN_THE_MONEY_PUTS):
            row = rows[0]
        elif (straddle_type == OptionTypes.IN_THE_MONEY_CALLS):
            row = rows[-1]

        row = row.text.replace(",", "").split(" ")
        # print(row)
        time_stamp = datetime.now().strftime("%Y-%m-%d")

        is_close_date = False
        close_date = self.get_close_date()
        if close_date:
            is_close_date = True

        try:
            put_price = float(row[self.PUT_PRICE_COLUMN])
            call_price = float(row[self.CALL_PRICE_COLUMN])
            strike = float(row[self.STRIKE_COLUMN])
            be = round((((put_price + call_price)/strike) * 100), 2)
            diff = (date - datetime.now()).days
        except ValueError:
            return None



        return { "type": straddle_type,
                 "strike" : strike,
                 "call" : call_price,
                 "put" : put_price,
                 "date" :  date.strftime("%Y-%m-%d"),
                 "be" : str(be) + "%",
                 "ticker": self.ticker,
                 "time_stamp": time_stamp,
                 "close_date": close_date,
                 "is_close_date": is_close_date,
                 "days_to_expiration": diff                
                 }

def get_straddles(driver ,ticker, conf):
    op = OptionPage(driver, conf)
    arr = []
    isFirst = True
    if conf["limit_dates"] is not None:
        op.dates = op.get_available_months()[:conf["limit_dates"]]
    else:
        op.dates = op.get_available_months()
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
        if cursor.count == 0:
            return False
        else:
            return True





def create_driver(conf):
    chrome_options = Options()  
    if conf["headless"]:
        chrome_options.add_argument("--headless")
    return  webdriver.Chrome(".//chromedriver", chrome_options=chrome_options)
    

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


def main(conn):
    print('Straddle Finder Selenium') 
    driver = create_driver(conf)
    if len(sys.argv) > 1:
        print("found it " + sys.argv[1])
        if sys.argv[1] == 'reverse':
            tickers.reverse()
        input()
    # tickers = ['aapl','spy']
    straddles = []
    op = OptionPage(driver=driver, conf=conf)
    for count, tick in enumerate(tickers):
        if not isSaved(conn=conn, ticker=tick):
            print("{} of {}, currently {}".format(str(count + 1), str(len(tickers)), tick))
            op.goto(ticker=tick, date=None)
            try:
                arr = get_straddles(driver=driver, ticker=tick, conf=conf)
                save_count = 0
                for straddle in arr:
                    if save_straddle(conn, straddle):
                        save_count += 1
                print("saved {} records".format(save_count))        
                op.dates = None
            except Exception as e:
                print("Unexpected error:", sys.exc_info()[0])
                print(e)

    driver_cleanup(driver)
    print('returning straddles')
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




   