from beatthemarket.blueprints.news.data import get_tickers_news
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import datetime
from beatthemarket.blueprints.portfolio.plClass import PLLedger

news = Blueprint('news', __name__, template_folder='templates',
                 url_prefix='/news')


@news.route('/')
@login_required
def show():
    tickers = PLLedger(current_user).get_tickers()

    if len(tickers) == 0:
        flash("MarketNews is available when holding records are available.",
              'error')
        return redirect(url_for('portfolio.holding'))

    tickers_articles = get_tickers_news(tickers)
    return render_template('news/display.html',
                           tickers_articles=tickers_articles)


@news.app_context_processor
def utility_processor():
    def convert_time(timestamp):
        # timestamp is epoch time in milliseconds
        converted_timestamp = datetime.datetime.fromtimestamp(timestamp / 1e3)
        article_time = converted_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return article_time

    return dict(convert_time=convert_time)
