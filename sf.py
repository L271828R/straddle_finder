import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from datetime import datetime
import random
from pymongo import MongoClient 
import time
from tickers import tickers


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
        if self.once == False:
            url = 'https://finance.yahoo.com/quote/__TICKER__/options?p=__TICKER__&straddle=true'
            url = url.replace('__TICKER__', ticker)
            self.driver.get(url)
            self.driver.implicitly_wait(8)
            self.once = True

        if date is not None:
            time.sleep(5)
            el_sel = Select(self.driver.find_element_by_tag_name("select"))
            el_sel.select_by_visible_text(date.strftime("%B %-d, %Y"))
        self.driver.implicitly_wait(3)
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
                 "days_to_expiration": diff                
                 }

def get_straddles(driver ,ticker, conf):
    op = OptionPage(driver, conf)
    arr = []
    isFirst = True
    if op.dates == None:
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

def main():
    print('Straddle Finder') 
    conf = { "random_time": True,
            "headless": True,
            "limit_dates": 5
    }
    chrome_options = Options()  
    if conf["headless"]:
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(".//chromedriver", chrome_options=chrome_options)
    # tickers = ['aapl','spy']
    straddles = []
    op = OptionPage(driver=driver, conf=conf)
    for count, tick in enumerate(tickers):
        print("{} of {}, currently {}".format(str(count + 1), str(len(tickers)), tick))
        op.goto(ticker=tick, date=None)
        try:
            arr = get_straddles(driver=driver, ticker=tick, conf=conf)
            straddles = straddles + arr
            op.dates = None
        except:
            pass

    driver_cleanup(driver)
    return straddles

if __name__ == '__main__':
    conn = None

    try: 
       conn = MongoClient() 
       print("Connected successfully!!!") 
    except:   
       print("Could not connect to MongoDB") 

    db = conn.database 
    collection = db.straddles 
    straddles = main()
    for straddle in straddles:
        if straddle is not None:
            cursor = collection.find({
                'strike':straddle['strike'],
                'date': straddle['date'],
                'type': straddle['type'],
                'ticker': straddle['ticker'],
                'days_to_expiration': straddle['days_to_expiration']
            })

            if cursor.count() == 0:
                collection.insert_one(straddle)
            else:
                pass
    print('done')

    # collection.insert_one(emp_rec1) 

    # cursor = collection.find({}) 
    # for record in cursor: 
    #     print(record) 




   