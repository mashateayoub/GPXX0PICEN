import requests
import json
import yfinance as yf
import pycron
import time
from datetime import datetime
from pytz import timezone

# Loads the config file
CONFIG = json.load(open("./config.json")) 
#Sets Python variables with the config file values
API_KEY, SECRET_KEY, BASE_URL = CONFIG["API_KEY"], CONFIG["SECRET_KEY"], CONFIG["BASE_URL"]  


def buy_operation(ticker, quantity):
    """
    Send a POST request to "/v2/orders" to create a new order
    :param ticker: stock ticker
    :param quantity:  quantity to buy
    :return: confirmation that the order to buy has been opened
    """
    url = BASE_URL + "/v2/orders"
    payload = json.dumps({
        "symbol": ticker,
        "qty": quantity,
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    })
    headers = {
        'APCA-API-KEY-ID': API_KEY,
        'APCA-API-SECRET-KEY': SECRET_KEY,
        'Content-Type': 'application/json'
    }
    return requests.request("POST", url, headers=headers, data=payload).json()

def close_position(ticker):
    """
    sends a DELETE request to "/v2/positions/" to liquidate an open position
    :param ticker: stock ticker
    :return: confirmation that the position has been closed
    """
    url = BASE_URL + "/v2/positions/" + ticker

    headers = {
        'APCA-API-KEY-ID': API_KEY,
        'APCA-API-SECRET-KEY': SECRET_KEY
    }
    return requests.request("DELETE", url, headers=headers).json()   


def get_positions():
    """
    sends a GET request to "/v2/positions" and returns the current positions that are open in our account
    :return: the positions that are held in the alpaca trading account
    """
    url = BASE_URL + "/v2/positions"
    headers = {
        'APCA-API-KEY-ID': API_KEY,
        'APCA-API-SECRET-KEY': SECRET_KEY,
    }
    return requests.request("GET", url, headers=headers).json()


def get_moving_averages(ticker):
    data = yf.download(ticker, period="3mo", interval='1h')  # Download the last 3months worht of data for the ticker
    data['SMA_4'] = data['Close'].rolling(window=4, min_periods=1).mean()   # Compute a 4-hours Simple Moving Average with pandas
    data['SMA_12'] = data['Close'].rolling(window=12, min_periods=1).mean()  # Compute a 12-hours Simple Moving Average with pandas
    SMA_4 = float(data.tail(1)["SMA_4"])  # Get the latest calculated 9 days Simple Moving Average
    SMA_12 = float(data.tail(1)["SMA_12"]) # Get the latest 30 days Simple Moving Average
    return SMA_4, SMA_12


if __name__ == "__main__":
    print("Starting the trading algorithm")
    while True:
        if pycron.is_now('*/1 * * * *', dt=datetime.now(timezone('EST'))):
            YFticker = "BTC-USD"
            ticker = "BTCUSD"
            SMA_4, SMA_12 = get_moving_averages(YFticker)
            print(get_positions())
            if SMA_4 > SMA_12:
                print("sup")
                # We should buy if we don't already own the stock
                if ticker not in [i["symbol"] for i in get_positions()]:
                    print("Currently buying", ticker)
                    buy_operation(ticker, 0.0001)
            if SMA_4 < SMA_12:
                print("min")
                # We should liquidate our position if we own the stock
                if ticker in [i["symbol"] for i in get_positions()]:
                    print("Currently liquidating our", ticker, "position")
                    close_position(ticker)
            time.sleep(60) # Making sure we don't run the logic twice in a minute
        else:
            time.sleep(20)  # Check again in 20 seconds