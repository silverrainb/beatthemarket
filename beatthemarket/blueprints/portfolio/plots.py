import plotly
import pandas as pd
import numpy as np
import json
import plotly.express as px


# PLOT2 PL TREEMAP ============================================================
def generate_pl_inputs(data):
    total_shares = float(data['total_shares'])
    total_cash = float(data['total_cash'])
    del data['total_cash']
    del data['total_shares']
    labels = [k for k in data.keys() if
              k not in ('total_shares', 'total_cash')]
    df = pd.DataFrame.from_dict(data).T
    df['Tickers'] = df.index
    df.reset_index(drop=True, inplace=True)
    df = df[
        ['upl', 'rpl', 'tpl', 'shares', 'pps', 'total_spending',
         'profit_rate',
         'Tickers', 'Avg. Volume', 'Volume']]
    df = df.replace(np.nan, 0)

    df_cash = df.copy()
    df_cash['AllocationType'] = 'Portfolio Distribution By Value %'
    df_cash['Allocation'] = (df['upl'] / float(total_cash)) * 100

    df_shares = df.copy()
    df_shares['AllocationType'] = 'Portfolio Distribution By Shares %'
    df_shares['Allocation'] = (df['shares'] / float(total_shares)) * 100

    df = pd.concat([df_cash, df_shares], axis=0)
    del df_cash
    del df_shares
    del data

    df['Allocation'] = df['Allocation'].astype(float).round(2)
    df['Investment'] = "My Investments"
    return df


def generate_pl_plot(data):
    data = generate_pl_inputs(data)
    plotly_fig = px.treemap(data, path=['Investment',
                                        'AllocationType',
                                        'Tickers'],
                            values='Allocation',
                            color='Allocation',
                            color_continuous_scale='Greys')
    plotly_fig.update_traces(textfont_size=14,
                             hovertemplate=
                             '<b>%{label}</b>' +
                             '<br>%{value:.2f}% <br>'
                             )
    plotly_fig.update_layout(coloraxis_showscale=False)
    plotly_fig.data[0].textinfo = 'label+text+value'
    graphJSON = json.dumps(plotly_fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


# PLOT3 EF_TBL ================================================================
def generate_ef_inputs(data):
    total_shares = float(data['total_shares'])
    total_cash = float(data['total_cash'])
    del data['total_cash']
    del data['total_shares']
    labels = [k for k in data.keys() if
              k not in ('total_shares', 'total_cash')]
    df = pd.DataFrame.from_dict(data).T
    df['Tickers'] = df.index
    df.reset_index(drop=True, inplace=True)
    df = df[
        ['upl', 'rpl', 'tpl', 'shares', 'pps', 'total_spending',
         'Tickers']]
    df = df.replace(np.nan, 0)

    df['Allocation'] = (df['total_spending'] / float(
        total_cash)) * 100
    df['Allocation'] = df['Allocation'].astype(float).round(2)

    pl_tickers = df['Tickers'].to_list()
    pl_weights = df['Allocation'].to_list()
    return pl_tickers, pl_weights
