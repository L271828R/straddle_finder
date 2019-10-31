# Description

Python program that scrapes Yahoo Finance (via the selenium library and driver) and obtains 
option prices for calls and  puts for at the money or near the money options for various 
maturities. 

The timeseries of the data is then saved in a MongoDb Database.

With these prices one can:

1. Obtain the volatility needed to implment a straddle strategy (long
and short) with its respective tenor (days until option expires)

2. Obtain the volatility trend of the straddle over a range of calendars.


# Dependecies

Python3
selenium
MongoClient

Needed Executable:

chrome driver (see below) 

# How do I install selenium

pip install selenium


# How do I install MongoClient

pip install pymongo 

# How do I get the chrome driver

You need to find a driver that supoorts your browser here:

https://chromedriver.chromium.org/

# Configuration

Look for the config.py file and make sure to add the location
to your chrome driver.


Also list your favorite tickers in tickers.py

# Great, I saved straddle data, but what about some help with reporting?

Kindly visit the follwoing repos for awesome reports based on the data saved here:

* straddle_report => Gives you the latest straddle or the time series of a straddle.
* earnings_report => This is for knowing what the straddle is for a company that will report earnings.

# How to run

python straddle_finder.py


![running straddle finder](https://i.imgur.com/IEqUWrp.jpg)



# Alternative run mehod (so as to run in parallel)

python straddle_finder.py -reverse


# Can you show me what gets saved in Mongo? What does the datamodel look like?


```javascript

{
	"_id" : ObjectId("5d5a0ec8b1845670465dd5ac"),
	"type" : "put-in-the-money",
	"strike" : 200,
	"call" : 3.15,
	"put" : 2.68,
	"date" : "2019-08-23",
	"be" : "2.92%",
	"ticker" : "gs",
	"time_stamp" : "2019-08-18",
	"close_date" : "2019-08-16",
	"is_close_date" : true,
	"days_to_expiration" : 4
}

```

* be = break even, this is the value of the put plus the value of the call devided by the at the money strike price.
* time_stamp = time the script was run
* close_date = time when the option last traded
* days_to_expiration = days (including weekends) until options expire.
* type = since options exactly at the money are rare, the type simply highights that if the straddle has in the money put or call legs.

# How do I look for my data in Mongo?

* mongo > use database > database.straddle.findOne({ticker:'gs'})


![running straddle finder](https://i.imgur.com/4zTn2B8.jpg)
