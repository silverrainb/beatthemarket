from flask import Blueprint, render_template, flash, redirect, url_for, \
    jsonify
from flask_login import login_required, current_user

from beatthemarket.blueprints.portfolio.efClass import EF
from beatthemarket.blueprints.portfolio.models import Holding, MarketSummary, \
    CurrentPrice, PL, Insight
from beatthemarket.blueprints.portfolio.forms import AddHoldingsForm
from beatthemarket.blueprints.portfolio.pl_helpers import serialize_pl
from beatthemarket.blueprints.portfolio.plClass import PLLedger
from beatthemarket.blueprints.portfolio.plots import generate_pl_plot, \
    generate_ef_inputs
import json

portfolio = Blueprint('portfolio', __name__, template_folder='templates',
                      static_folder='static', url_prefix='/portfolio')


@portfolio.route('/holding', methods=['GET', 'POST'])
@login_required
def holding():
    form = AddHoldingsForm()
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if
                k not in ("csrf_token", 'next')}
        data['type'] = data['type'].capitalize()
        data['ticker'] = data['ticker'].upper()
        data['user_id'] = current_user.id

        if data['type'] == "Sell":
            data['rpl'] = data['quantity'] * data['price']
        else:
            data['rpl'] = 0

        if data['type'] == "Buy":
            data['total_spending'] = data['quantity'] * data['price']
        else:
            data['total_spending'] = 0
        holding_data = Holding(**data)
        holding_data.save()

        # Update market data using celery
        Holding.initialize_update_market_data()

        flash('Your holding record has been saved.', 'success')

        return redirect(url_for('portfolio.holding'))

    holding_records = Holding.query.filter(
        Holding.user_id == current_user.id).all()
    return render_template('portfolio/holding.html', form=form,
                           holding_records=holding_records)


@portfolio.route('/holding/<int:id>/delete', methods=['POST'])
@login_required
def delete_holding(id):
    record = Holding.query.get_or_404(id)
    record.delete()
    flash("The record has been successfully removed.", 'success')
    return redirect(url_for('portfolio.holding'))


@portfolio.route('/pl')
@login_required
def pl():
    my_pl = PLLedger(current_user)
    tickers = my_pl.get_tickers()

    if len(tickers) == 0:
        flash("P&L is available when holding records are available.", 'error')
        return redirect(url_for('portfolio.holding'))

    # Get current price of the tickers the user own
    current_prices_db = CurrentPrice.query.order_by(
        CurrentPrice.id.desc()).first().data
    current_prices = dict(
        [(keys, current_prices_db[keys]) for keys in tickers])

    # Fetch the latest records from market_summ of tickers user own
    market_dicts_db = MarketSummary.query.order_by(
        MarketSummary.id.desc()).first().data
    market_dicts = dict(
        [(keys, market_dicts_db[keys]) for keys in tickers])

    complete_pl, total_shares, total_cash, pl_for_save = my_pl.get_complete_pl(
        market_dicts, current_prices)

    # TODO REFACTOR REQUIRED update this to UPDATE not SAVE...
    save_pl = PL(user_id=current_user.id,
                 data=json.dumps(pl_for_save, default=serialize_pl))
    save_pl.save()
    print("=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*P&L saved!")

    plot = generate_pl_plot(pl_for_save)

    return render_template('portfolio/pl.html',
                           complete_pl=complete_pl,
                           total_shares=total_shares,
                           total_cash=total_cash,
                           plot=plot)


@portfolio.route('/visualization')
@login_required
def visualization():
    return render_template('portfolio/visualization.html')


@login_required
@portfolio.route('/visualization/data')
def visualization_data():
    pl_data = PL.query.filter(PL.user_id == current_user.id).order_by(
        PL.id.desc()).first()

    # If holding record is empty
    if pl_data is None:
        flash("Insight is available when holding records are available.",
              'error')
        return redirect(url_for('portfolio.holding'))

    data = json.loads(pl_data.data)
    pl_tickers, pl_weights = generate_ef_inputs(data)

    # Create Cache
    # None if not exist
    ef_data = Insight.query.filter(Insight.ticker == str(pl_tickers)).order_by(
        Insight.id.desc()).first()
    if ef_data is not None:
        ef_dict = json.loads(ef_data.data)
    else:
        ef_instance = EF(duration=5,
                         pl_data=data,
                         pl_tickers=pl_tickers,
                         pl_weights=pl_weights,
                         num_ports=15000)  # 15000
        # TODO in 2nd Capstone: time bar according to job progress
        tbl_contents, ef_contents, sim_contents, alloc_contents = ef_instance.generate_ef_viz()
        # create db obj
        ef_keys = ['tbl', 'ef', 'sim', 'alloc']
        ef_vals = [tbl_contents, ef_contents, sim_contents, alloc_contents]
        ef_dict = {k: v for k, v in zip(ef_keys, ef_vals)}
        # save
        # TODO REFACTOR REQUIRED update this to UPDATE not SAVE...
        save_ef = Insight(ticker=str(pl_tickers),
                          data=json.dumps(ef_dict, default=serialize_pl))
        save_ef.save()
        print("=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*EF saved!")

    return jsonify(tbl=ef_dict['tbl'],
                   ef=ef_dict['ef'],
                   sim=ef_dict['sim'],
                   alloc=ef_dict['alloc'])
