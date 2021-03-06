# -*- coding: utf-8 -*-
"""Final Slackbot.ipynb

Automatically generated by Colaboratory.

"""

pip install slackclient
pip install python-dotenv
pip install yfinance --upgrade --no-cache-dir
pip install slack_sdk

# Dependency download process explained here: https://www.youtube.com/watch?v=vf1m1ogKYrg

import yfinance as yf
import pandas as pd
import slack
import time

SLACK_TOKEN="SLACK_TOKEN"

'''
Written by Siddharth Cherukupalli
'''

# Apex Google Sheets Setup

sheet_id = "SHEET_ID"
sheet_name = "SHEET_NAME"
holdingsUrl = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
holdingsSheet = pd.read_csv(holdingsUrl)

grossReturnSheet_name = "Gross_Returns"
grossReturnUrl = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={grossReturnSheet_name}"
grossReturnSheet = pd.read_csv(grossReturnUrl)

NUM_OF_PORTFOLIO_TICKERS = 0
for idx in holdingsSheet['Holdings ']:
  if (idx != 'Only Tickers Above this Row will be fed into SlackBot'):
      NUM_OF_PORTFOLIO_TICKERS += 1
  
def portfolioStats():
  # Original Google Sheet URL: INSERT HERE
  table = "----------Apex Portfolio Statistics----------\n";
  for num in range(NUM_OF_PORTFOLIO_TICKERS):
    table += holdingsSheet['Holdings '][num] + " P/L: " + holdingsSheet['P/L'][num] + "\n"
  table += "Portfolio Gross Return: " + grossReturnSheet['Gross Returns'][0] + "\n\n"
  return table

print(portfolioStats())
#Add any tickers to this to make sure current prices and Day over Day changes are shown 
tickers = []
for num in range(NUM_OF_PORTFOLIO_TICKERS):
  tickers.append(holdingsSheet['Holdings '][num])

indices = ["^GSPC'", "^RUT", "^DJI"]

# Get current price

def getPrices(tickers, indices):
  
  res = "--------------------Major Indices-------------------- \n" 
  for index in indices:
    index = yf.Ticker(index)
    closePrice = index.info['previousClose']
    currentPrice = index.info['regularMarketPrice']
    percentage = (currentPrice/closePrice -1) * 100
    strFormat = "{:.2f}".format(percentage) + "%"
    res += str(index.info['shortName']) + " Current Price: $" + str(currentPrice)
    res += " || 1d change: " + strFormat + "\n"

  res += "\n--------------------Current Holdings-------------------- \n" 
  for tick in tickers:
    ticker = yf.Ticker(tick)
    currentPrice = str(ticker.info['regularMarketPrice'])
    res += ticker.ticker + " Current Price: $" + currentPrice + "\n"
  return res

#Day over Day Price Changes

def getChanges(tickers):
  result = "--------------------Day over Day Changes-------------------- \n"
  for tick in tickers:
    ticker = yf.Ticker(tick)
    closePrice = ticker.info['previousClose']
    currentPrice = ticker.info['regularMarketPrice']
    percentage = (currentPrice/closePrice -1) * 100
    strFormat = "{:.2f}".format(percentage) + "%"
    result += ticker.ticker + " 1d change: " + strFormat + "\n"
  return result

maxStories = 3;
SECONDS_IN_A_MINUTE=60
MINUTES_IN_A_HOUR=60
SECONDS_IN_A_HOUR=SECONDS_IN_A_MINUTE * MINUTES_IN_A_HOUR
HOURS_IN_A_DAY=24
SECONDS_IN_A_DAY=SECONDS_IN_A_HOUR * HOURS_IN_A_DAY
def getNews(tickers):
  res = "--------------------Current News-------------------- \n"
  for tick in tickers:
    storyCount = 1
    ticker = yf.Ticker(tick)
    news = ticker.news
    res += "-----" + ticker.ticker + " News----- \n"
    for elem in news:
      link = elem['link']
      publisher = elem['publisher']
      title = elem['title']
      timeDiff = time.time() - elem['providerPublishTime']
      if (storyCount <= maxStories):
        if (timeDiff <= (SECONDS_IN_A_DAY)): 
         res += "\n" + publisher + "\n" + title + "\n" + link + "\n\n"
         storyCount += 1 
    
  return res

def run_lambda(event, context):
  message = "<!channel> \n"
  message += portfolioStats()
  message += getPrices(tickers, indices) + "\n" 
  message += getChanges(tickers) + "\n" 
  message += getNews(tickers)
  client = slack.WebClient(token=SLACK_TOKEN)
  client.chat_postMessage(channel = "#daily-slackbot", text=message)

  return {}
