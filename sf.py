import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from datetime import datetime
import random


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
    
    def goto(self, ticker):
        url = 'https://finance.yahoo.com/quote/__TICKER__/options?p=__TICKER__&straddle=true'
        url = url.replace('__TICKER__', ticker)
        self.driver.get(url)
        if self.conf['random_time'] == True:
            self.driver.implicitly_wait(random.randrange(5, 10))
        else:
            self.driver.implicitly_wait(3)
        self.ticker = ticker

    def get_available_months(self):
        el_sel = Select(self.driver.find_element_by_tag_name("select"))
        options = el_sel.options
        dates = []
        for op in options:
            dates.append(datetime.strptime(op.text, "%B %d, %Y"))
        return dates
    
    def get_straddle(self, straddle_type = 'put-in-the-money'):
        el_table = self.driver.find_element_by_css_selector("table.straddles")
        rows = el_table.find_elements_by_css_selector("tr." + straddle_type)
        if (straddle_type == 'put-in-the-money'):
            row = rows[0]
        else:
            row = rows[-1]

        row = row.text.replace(",", "").split(" ")
        # print(row)
        time_stamp = datetime.now().strftime("%y-%m-%d")
        try:
            put_price = float(row[self.PUT_PRICE_COLUMN])
            call_price = float(row[self.CALL_PRICE_COLUMN])
            strike = float(row[self.STRIKE_COLUMN])
            be = round((((put_price + call_price)/strike) * 100), 2)
            date = self.get_available_months()[0].strftime("%Y-%m-%d")
        except ValueError:
            return {}



        return { "type": straddle_type,
                 "strike" : strike,
                 "call" : call_price,
                 "put" : put_price,
                 "date" :  date,
                 "be" : str(be) + "%",
                 "ticker": self.ticker,
                 "time_stamp": time_stamp                
                 }

def get_straddles(driver ,ticker, conf):
   op = OptionPage(driver, conf)
   op.goto(ticker)
   results = op.get_straddle(OptionTypes.IN_THE_MONEY_PUTS)
   print(results)
   results = op.get_straddle(OptionTypes.IN_THE_MONEY_CALLS)
   print(results)


if __name__ == '__main__':
   print('hello Straddles') 
   chrome_options = Options()  
   chrome_options.add_argument("--headless")
   driver = webdriver.Chrome(".//chromedriver", chrome_options=chrome_options)
   tickers = ['aapl', 'tsla', 'goog', 'bidu', 'bynd', 'eght', 'amd', 'feye', 'grub', 'zen', 'ge']
   conf = { "random_time": False }
   for tick in tickers:
       get_straddles(driver=driver, ticker=tick, conf=conf)
   driver.close()
   driver.quit()


   