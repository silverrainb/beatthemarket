from flask import url_for
from flask_login import current_user

from beatthemarket.blueprints.portfolio.plClass import PLLedger
from beatthemarket.blueprints.portfolio.plots import generate_pl_plot
from lib.tests import assert_status_with_message, ViewTestMixin
from beatthemarket.blueprints.portfolio.models import Holding, MarketSummary, \
    CurrentPrice, PL, Insight
import pytest


class TestHolding(ViewTestMixin):
    def test_holding(self):
        self.login()

        # Holding.query.filter(Holding.user_id == 1).all()
        holding = {
            'user_id': 1,
            'type': 'buy',
            'ticker': 'MSFT',
            'quantity': 1,
            'date': '2020-02-02',
            'price': 100,
            'rpl': 0,
            'total_spending': 100,
        }
        response = self.client.post(url_for('portfolio.holding'),
                                    data=holding, follow_redirects=True)

        html = response.get_data(as_text=True)
        assert_status_with_message(200, response, "Add My Holdings")
        assert "Your holding record has been saved" in html

    def test_delete_holding(self):
        self.login()

        response = self.client.post('/holding/1/delete')
        # TODO this is 404 right now. WhY is 404 always 200:
        html = response.get_data(as_text=True)
        # The record has been successfully removed.
        pass


class TestPL(ViewTestMixin):
    def test_pl(self):
        response = self.client.get(url_for('portfolio.pl'))
        assert_status_with_message(302, response, "Redirecting...")

    def test_pl_with_login(self):
        # self.login()
        # # self.tickers=['MSFT']
        # # complete_pl = pass
        # # total_shares = pass
        # # total_cash = pass
        # Holding.query.filter(Holding.user_id == 1).all()
        # pytest.set_trace()
        #
        # my_pl = PLLedger(current_user)
        # tickers = ['MSFT']
        # current_prices_db = CurrentPrice.query.order_by(
        #     CurrentPrice.id.desc()).first().data
        # current_prices = dict(
        #     [(keys, current_prices_db[keys]) for keys in tickers])
        #
        # # Fetch the latest records from market_summ of tickers user own
        # market_dicts_db = MarketSummary.query.order_by(
        #     MarketSummary.id.desc()).first().data
        # market_dicts = dict(
        #     [(keys, market_dicts_db[keys]) for keys in tickers])
        #
        # complete_pl, total_shares, total_cash, pl_for_save = my_pl.get_complete_pl(
        #     market_dicts, current_prices)
        #
        # plot = generate_pl_plot(pl_for_save)
        #
        # data = {'complete_pl': complete_pl,
        #         'total_shares': total_shares,
        #         'total_cash': total_cash,
        #         'plot': plot}
        # response = self.client.get(url_for('portfolio.pl'), data=data,
        #                            follow_redirects=True)
        # pytest.set_trace()
        pass

    def test_visualization(self):
        pass

    def test_visualization_data(self):
        pass
