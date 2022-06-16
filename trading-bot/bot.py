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