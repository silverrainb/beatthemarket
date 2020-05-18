import pandas as pd
from bs4 import BeautifulSoup
import requests


def symbols_sp500():
    """
    scrape from wikipedia for the current S&P500 symbols
    :return:
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        # cols
        stocks = soup.find(id="constituents")
        ths = stocks.find_all('th')
        cols = []
        for th in ths:
            cols.append(th.text)
        cols = [item.strip() for item in cols if str(item)]
        # df
        tbl_contents = soup.find_all('table')
        tbl_contents_arr = pd.read_html(str(tbl_contents))[0].values
        tbl_df = pd.DataFrame.from_records(tbl_contents_arr, columns=cols)
        return tbl_df[['Security', 'Symbol']]

    except Exception as e:
        print(e)


def symbols_nasdaq100():
    """
    scrape from wikipedia for the current NASDAQ100 symbols
    :return:
    """
    try:
        url = 'https://en.wikipedia.org/wiki/NASDAQ-100'
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        # get table
        tbl = soup.find(id="constituents")
        # parse table
        tbl_dict = parse_table(tbl)
        # parse columns
        ths = tbl_dict['head'][0].find_all('th')
        cols = []
        for th in ths:
            cols.append(th.text)
        cols = [item.strip() for item in cols if str(item)]
        # parse contents
        trs = tbl_dict['body']
        df_contents = []
        for tr in trs:
            df_contents.append(tr.text)
        df_contents = [item.strip() for item in df_contents if str(item)]
        df_contents = [item.split('\n') for item in df_contents if str(item)]
        df = pd.DataFrame(df_contents, columns=cols)
        return df
    except Exception as e:
        print(e)


def parse_table(table):
    head_body = {'head': [], 'body': []}
    for tr in table.select('tr'):
        if all(t.name == 'th' for t in tr.find_all(recursive=False)):
            head_body['head'] += [tr]
        else:
            head_body['body'] += [tr]
    return head_body


def tickers_to_db():
    sp = symbols_sp500()
    sp.columns = ['Company', 'Ticker']
    nsdq = symbols_nasdaq100()
    alldf = pd.concat([nsdq, sp], axis=0).sort_values(
        'Ticker').drop_duplicates(subset='Ticker')
    alldf['Tag'] = alldf['Ticker'].astype(str) + ", " + alldf[
        'Company'].astype(str)

    alldf[["Tag", "Ticker"]].to_csv('src/tickers.csv', index=False)
    # save_symbols = Ticker(company=alldf['Company'], ticker=alldf['Ticker'])
    # save_symbols.save()
