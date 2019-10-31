# Description

Python program that scrapes Yahoo Finance (via the selenium library and driver) and obtains 
option prices for calls and  puts for at the money or near
the money options. 

The timeseries of the data is then saved in a MongoDb Database.

With these prices one can:

1. Obtain the volatility needed to implment a straddle strategy (long
and short) with its respective tenor (days until option expires)

2. Obtain the volatility trend of the straddle over a range of calendars.


# Dependecies

Python3
selenium
chrome driver

# How do I install selenium

pip install selenium

# How do I get the chrome driver

You need to find a driver that supoorts your browser here:

http:some.url.com

# Configuration

Look for the config.py file and make sure to add the location
to your chrome driver.


Also liskt your favorite tickers in tickers.py

# Great, I saved straddle data, but what about some help with reporting?

Kindly visit the follwoing repos for awesome reports:

straddle_report => Gives you the latest straddle or the time series of a straddle.
earnings_report => This is for knowing what the straddle is for a company that will report earnings.

# How to run

python sf.py


![running straddle finder](https://i.imgur.com/ef2GRUD.jpg)



# Alternative run mehod (so as to run in parallel)

python sf.py -reverse
