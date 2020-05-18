import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
from sqlalchemy import create_engine, update
from config import settings
from beatthemarket.blueprints.portfolio.models import MarketSummary, \
    CurrentPrice
from sqlalchemy.orm.attributes import flag_modified

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)


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


def save_quote(app):
    tickers = all_tickers()
    market_dicts, current_prices = fetch_all(tickers)

    with app.app_context():
        new_current_prices_data_obj = CurrentPrice(data=current_prices)
        new_market_data_obj = MarketSummary(data=market_dicts)
        try:
            new_current_prices_data_obj.save()
            new_market_data_obj.save()
            print("=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*current price saved!",
                  new_current_prices_data_obj.data)
            print("=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*market summary saved!",
                  new_market_data_obj.data)
        except Exception as e:
            print(e)

    # TODO Can this be fixed to Update? Constantly failed at it.
    # with app.app_context():
    #     if CurrentPrice.query.count() > 0:
    #         # Get first row of the each db
    #         curr_price_obj = CurrentPrice.query.filter(
    #             CurrentPrice.id == 1).first()
    #         # Get current objects data
    #         curr_price_obj_data = curr_price_obj.data
    #         # Swap the data with new current_prices
    #         curr_price_obj_data = current_prices
    #         # flag modified.
    #         flag_modified(curr_price_obj, "data")
    #         # let's commit
    #         db.session.merge(curr_price_obj)
    #         db.session.flush()
    #         db.session.commit()
    #         print(
    #             f"========@{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} TEST Current Price has been updated========")
    #     elif MarketSummary.query.count() > 0:
    #         curr_market_obj = MarketSummary.query.filter(
    #             MarketSummary.id == 1).first()
    #         curr_market_obj_data = curr_market_obj.data
    #         curr_market_obj_data = market_dicts
    #         flag_modified(curr_market_obj, "data")
    #         db.session.merge(curr_market_obj)
    #         db.session.flush()
    #         db.session.commit()
    #         print(
    #             f"========@{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} TEST Market Summ has been updated========")
    #     else:
    #         new_current_prices_data_obj.save()
    #         new_market_data_obj.save()
