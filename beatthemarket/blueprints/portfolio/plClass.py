from functools import reduce
import pandas as pd
from sqlalchemy import create_engine
from beatthemarket.blueprints.portfolio.pl_helpers import merge_dicts
from config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)


class PLLedger:

    def __init__(self, current_user):
        self.current_user = current_user

    def get_pl(self, current_prices):
        user_holding_records = self.holding_df()
        tickers = user_holding_records.ticker.unique().tolist()
        pl_dict = {}
        for ticker in tickers:
            pl_dict[ticker] = self.ledger(user_holding_records, ticker,
                                          current_prices)
        return pl_dict

    def get_tickers(self):
        user_holding_records = self.holding_df()
        tickers = user_holding_records.ticker.unique().tolist()
        return tickers

    def holding_df(self):
        query = f"SELECT id, user_id, type, ticker, quantity, price, total_spending, rpl, date " \
                f"FROM holdings WHERE user_id = {self.current_user.id}"
        holdings_df = pd.read_sql(
            query,
            con=engine,
            parse_dates=['date'])
        return holdings_df

    def ledger(self, user_holding_records, ticker, current_prices):
        df = user_holding_records[user_holding_records.ticker == f"{ticker}"]

        def get_shares(df):
            try:
                shares = df[df.type == 'Buy']['quantity'].sum() - \
                         df[df.type == 'Sell']['quantity'].sum()
                return shares
            except ValueError:
                print("Bid quantity must be greater than Ask quantity")

        def get_ticker_current_price(current_prices, ticker):
            ticker_price = 0
            for key, val in current_prices.items():
                if key == ticker:
                    ticker_price = float(val)
            return ticker_price

        current_ticker_price = get_ticker_current_price(current_prices, ticker)
        shares = get_shares(df)
        upl = current_ticker_price * shares
        rpl = df[df.rpl.notnull()].rpl.sum()

        pps = round(upl / shares, 2)
        tpl = rpl + upl

        total_spending = df.total_spending.sum()
        avg_purchase_price = total_spending / shares

        profit_rate = (current_ticker_price / avg_purchase_price - 1) * 100
        keys = ['rpl', 'shares', 'upl', 'pps', 'tpl', 'total_spending',
                'avg_purchase_price', 'current_ticker_price', 'profit_rate']
        vals = [round(rpl, 2), shares, round(upl, 2), pps, round(tpl, 2),
                total_spending, avg_purchase_price, current_ticker_price,
                round(profit_rate, 2)]
        result = dict(zip(keys, vals))
        return result

    def get_total(self, complete_pl):
        """insert dict"""
        user_pl_df = pd.DataFrame.from_records(complete_pl).T
        total_shares = user_pl_df.shares.sum()
        total_invested_cash = user_pl_df.upl.sum()
        return total_shares, total_invested_cash

    def get_complete_pl(self, market_dicts, current_prices):
        # get P&L
        pl_dicts = self.get_pl(current_prices)
        # Merge the market and pl data to create complete PL
        complete_pl = reduce(merge_dicts, [market_dicts, pl_dicts])
        # Calculate all tickers' sum of shares and cash
        total_shares, total_cash = self.get_total(complete_pl)
        # Create PL for saving in DB including total_shares, total_cash
        # We need these 2 variable as independent to pass in jinja
        pl_for_save = complete_pl.copy()
        pl_for_save['total_shares'] = total_shares
        pl_for_save['total_cash'] = total_cash
        return complete_pl, total_shares, total_cash, pl_for_save
