import time
import random
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from datetime import datetime

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
        if self.conf['verbose']:
            print('GOING TO:' ,url, date)
        self.driver.get(url)
        self.driver.implicitly_wait(8)
        self.once = True
        self.ticker = ticker

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
            if len(close_date) == 6:
                close_date = datetime.now().strftime("%Y-%m-%d")
            else:
                try:
                    close_dt = datetime.strptime(close_date, "%B %d %I:%M%p")
                except ValueError:
                    today = datetime.now()
                    month = today.month
                    day   = today.day
                    year  = today.year
                    hour = 16
                    sdate = "{}-{}-{} {}".format(year, month, day, hour)
                    close_dt = datetime.strptime(sdate, "%Y-%m-%d %M")

                close_date = close_dt.strftime( str(datetime.now().year) + "-%m-%d")
        return close_date



    def get_straddle(self, straddle_type, date):
        el_table = self.driver.find_element_by_css_selector("table.straddles")
        rows = el_table.find_elements_by_css_selector("tr." + straddle_type)
        try:
            if (straddle_type == OptionTypes.IN_THE_MONEY_PUTS):
                row = rows[0]
            elif (straddle_type == OptionTypes.IN_THE_MONEY_CALLS):
                row = rows[-1]
        except IndexError:
            return None

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


