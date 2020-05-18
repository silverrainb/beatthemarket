from beatthemarket.extensions import celery
import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
from sqlalchemy import create_engine
from config import settings
from beatthemarket.blueprints.portfolio.models import MarketSummary, \
    CurrentPrice

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)


@celery.task()
def update_market_data():
    """
    This task checks whether the data is inplace otherwise fetch and update right away
    this function is called from portfolio/models classmethod
    and used by view function in portfolio/views
    :return:
    """
    try:
        save_quote_celery()
        print("CELERY UPDATE MARKET DATA TASK SUCCESS")
    except (KeyboardInterrupt, SystemExit):
        pass
    return None


def all_tickers():
    """
    Get all tickers that ALL users own in beatthemarket
    Runs every 1 minute
    """
    query = f"SELECT distinct(ticker) FROM holdings"
    df = pd.read_sql(
        query,
        con=engine,
        parse_dates=['date'])
    df_list = df.values.tolist()
    ticker_list = []
    for tickers in df_list:
        for ticker in tickers:
            ticker_list.append(ticker)
    return ticker_list


def fetch(ticker):
    url = f'http://finance.yahoo.com/quote/{ticker}?p={ticker}'
    res = requests.get(url)
    # Parse HTML
    soup = (BeautifulSoup(res.content, 'html.parser'))
    # Get Table
    table1 = soup.find_all('table')[0]
    table2 = soup.find_all('table')[1]
    tbl1 = pd.read_html(str(table1))[0].values
    tbl2 = pd.read_html(str(table2))[0].values
    tbl_concat = np.concatenate((tbl1, tbl2))
    # Create Market Dict
    market_dict = {a: b for a, b in tbl_concat}

    # if nan, assign 0
    def convert_nan(v):
        if isinstance(v, float):
            if v > 0:
                v = v
            else:
                v = 0
        return v

    market_dict = {k: convert_nan(v) for k, v in market_dict.items()}

    # Get Current Prices
    quote = []
    quote_header_info = soup.find("div", {"id": "quote-header-info"})
    spans = quote_header_info.find_all('span')
    for span in spans:
        quote.append(span.get_text())
    # remove , in 1,000
    price = quote[1].replace(",", "")
    market_dict['Current Price'] = float(price)

    return market_dict


def fetch_all(tickers):
    market_dicts = {}
    current_prices = {}
    for ticker in tickers:
        market_dicts[f'{ticker}'] = fetch(ticker)
        current_prices[f'{ticker}'] = market_dicts[f'{ticker}'][
            'Current Price']

    return market_dicts, current_prices


def save_quote_celery():
    tickers = all_tickers()
    market_dicts, current_prices = fetch_all(tickers)

    new_current_prices_data_obj = CurrentPrice(data=current_prices)
    new_market_data_obj = MarketSummary(data=market_dicts)
    try:
        # TODO REFACTOR REQUIRED: this should not be save but UPDATE
        new_current_prices_data_obj.save()
        new_market_data_obj.save()
        print("=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*current price saved!",
              new_current_prices_data_obj.data)
        print("=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*market summary saved!",
              new_market_data_obj.data)
    except Exception as e:
        print(e)


@celery.task
def dummy_task():
    return "OK"
