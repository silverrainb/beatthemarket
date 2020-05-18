import numpy as np
import pandas as pd
import pandas_datareader as web
from datetime import date
from dateutil.relativedelta import relativedelta
import scipy.optimize as optimize
import plotly
import plotly.graph_objects as go
import json


class EF:

    def __init__(self, duration, pl_data, pl_tickers, pl_weights, num_ports):
        self.pl_data = pl_data
        self.tickers = pl_tickers
        self.weights = pl_weights
        self.end = date.today()
        self.start = self.end - relativedelta(years=duration)
        self.num_ports = num_ports
        self.num_portfolios = 100
        self.risk_free_rate = 0.0152

    def get_data(self):
        data = {}
        for ticker in self.tickers:
            data[ticker] = web.DataReader(ticker, 'yahoo',
                                          self.start.strftime('%Y-%m-%d'),
                                          self.end.strftime('%Y-%m-%d'))[
                'Adj Close']
        df = pd.DataFrame.from_dict(data)
        return df

    def get_return(self):
        df = self.get_data()
        returns = df.pct_change()
        mean_returns = returns.mean()
        cov_matrix = returns.cov()

        return returns, mean_returns, cov_matrix

    def my_current_portfolio(self):
        df = self.get_data()
        # Re-balance - normalization
        weights = np.array(self.weights / np.sum(self.weights))

        ## Expected Return
        exp_ret = np.sum(df.pct_change().mean() * weights) * 252

        ## Expected Volatility
        exp_vol = np.sqrt(
            np.dot(weights.T, np.dot(df.pct_change().cov() * 252, weights)))

        ## Sharpe Ratio
        SR = exp_ret / exp_vol

        output = ["Current Portfolio", round(exp_ret * 100, 2),
                  round(exp_vol * 100, 2), round(SR, 4)]
        return output

    def generate_ef_viz(self):
        my_pl_output = self.my_current_portfolio()
        df = self.get_data()
        returns, mean_returns, cov_matrix = self.get_return()
        annual_volatility, annual_return, expected_volatility, expected_return, \
        min_expected_volatility, min_expected_return, max_sharpe, min_vol, \
        frontier_vol, frontier_y, ef_df, \
        max_sharpe_allocation, min_vol_allocation = self.display_ef(
            mean_returns,
            cov_matrix,
            self.risk_free_rate,
            self.num_portfolios,
            returns, df,
            self.tickers)

        tbl_contents = \
            [list(e) for e in zip(*[my_pl_output,
                                    [
                                        "Maximum Sharpe Ratio Portfolio",
                                        round(expected_return * 100,
                                              2),
                                        round(
                                            expected_volatility * 100,
                                            2),
                                        round(
                                            expected_return / expected_volatility,
                                            4)],
                                    ["Minimum Volatility Portfolio",
                                     round(
                                         min_expected_return * 100,
                                         2),
                                     round(
                                         min_expected_volatility * 100,
                                         2),
                                     round(
                                         min_expected_return / min_expected_volatility,
                                         4)],
                                    ])]

        # PLOT 1 PORTFOLIO COMPARISON =========================================
        tbl_fig = go.Figure()
        tbl_fig.add_trace(go.Table(
            header=dict(
                values=["Portfolio", "Expected Return", "Expected Volatility",
                        "Sharpe Ratio"],
                font=dict(size=15),
                align="left"
            ),
            cells=dict(
                values=tbl_contents,
                align="left")
        ))
        tbl_fig.update_layout(
            title={'text': "Portfolio Comparison"},
            titlefont=dict(size=36),
            height=250
        )

        TBLgraphJSON = json.dumps(tbl_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # PLOT 2 ALLOCATION TABLE ===========================================
        weights_contents = \
            [list(e) for e in zip(*[
                ["Maximum Sharpe Ratio Portfolio"] + max_sharpe.x.tolist(),
                ["Minimum Volatility Portfolio"] + min_vol.x.tolist()
                                    ])]
        alloc_fig = go.Figure()
        alloc_fig.add_trace(go.Table(
            header=dict(
                values=['Portfolio'] + max_sharpe_allocation.columns.to_list(),
                font=dict(size=15),
                align="left"
            ),
            cells=dict(
                values=weights_contents,
                align="left")
        ))
        alloc_fig.update_layout(
            title={'text': "Allocation Weights"},
            titlefont=dict(size=36),
            height=250
        )

        ALLOCgraphJSON = json.dumps(alloc_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # PLOT 3 EF PLOT ======================================================
        vol_arr, ret_arr, sharpe_arr = self.run_simulation(df)
        ef_fig = go.Figure()

        # Mark the tickers position
        ef_fig.add_trace(go.Scatter(
            x=annual_volatility * 100,
            y=annual_return * 100,
            mode="markers",
            marker=dict(
                size=16,
                symbol='diamond',
                color='orange'
            ),
            name="Ticker",
            text=self.tickers,
            # TODO check if this worked https://plotly.com/python/text-and-annotations/
            # textposition="bottom center",
            hovertemplate=
            '<b>Ticker</b>: %{text}' +
            '<br><b>Expected Return</b>: %{y:.2f}%<br>' +
            '<b>Risk</b>: %{x:.2f}%'
        ))

        # Simulation
        ef_fig.add_trace(go.Scatter(
            x=vol_arr * 100,
            y=ret_arr * 100,
            mode="markers",
            marker=dict(
                color=sharpe_arr,
            ),
            name="EF Simulation",
            text=sharpe_arr,
            hovertemplate=
            '<b>Simulated Allocation</b>' +
            '<br><b>Sharpe Ratio</b>: %{text:.2f}' +
            '<br><b>Expected Return</b>: %{y:.2f}%<br>' +
            '<b>Risk</b>: %{x:.2f}%'

        ))

        # Frontier line
        ef_fig.add_trace(go.Scatter(
            x=ef_df['Standard Deviation'] * 100,
            y=ef_df['Expected Return'] * 100,
            mode='lines+markers',
            line=dict(color="black"),
            name="EF Line",
            text=ef_df['Sharpe Ratio'],
            hovertemplate=
            '<b>Efficient Frontier Line</b>' +
            '<br><b>Sharpe Ratio</b>: %{text:.2f}' +
            '<br><b>Expected Return</b>: %{y:.2f}%<br>' +
            '<b>Risk</b>: %{x:.2f}%'
        ))
        # Maximum Sharpe Ratio Portfolio Allocation
        ef_fig.add_trace(go.Scatter(
            x=[expected_volatility * 100],
            y=[expected_return * 100],
            mode="markers",
            name="Max. SR. ALLOC.",
            marker=dict(
                size=16,
                symbol='star',
                color='green'
            ),
            text=[expected_return / expected_volatility],
            hovertemplate=
            '<b>Maximum Sharpe Ratio Portfolio ALLOC</b>' +
            '<br><b>Sharpe Ratio</b>: %{text:.2f}' +
            '<br><b>Expected Return</b>: %{y:.2f}%<br>' +
            '<b>Risk</b>: %{x:.2f}%'
        ))

        # Minimum Volatility Portfolio Allocation
        ef_fig.add_trace(go.Scatter(
            x=[min_expected_volatility * 100],
            y=[min_expected_return * 100],
            mode="markers",
            name="Min. Risk ALLOC.",
            marker=dict(
                size=16,
                symbol='x-dot',
                color='blue'
            ),
            text=[min_expected_volatility / min_expected_return],
            hovertemplate=
            '<b>Minimum Volatility Portfolio ALLOC</b>' +
            '<br><b>Sharpe Ratio</b>: %{text:.2f}' +
            '<br><b>Expected Return</b>: %{y:.2f}%<br>' +
            '<b>Risk</b>: %{x:.2f}%'
        ))
        tbl_fig.update_layout(
            title="Portfolio Comparison",

        )
        ef_fig.update_layout(
            xaxis_title="Standard Deviation",
            yaxis_title="Expected Return",
            title="Efficient Frontier",
            titlefont=dict(size=36),
            # legend_title='<b>Tickers</b>',
            showlegend=True,
            height=700,

            xaxis=dict(
                # type='linear',
                ticksuffix='%'),
            yaxis=dict(
                # type='linear',
                # range=[1, 100],
                ticksuffix='%'),
            # hovermode="x"
        )

        EFgraphJSON = json.dumps(ef_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # PLOT 4 Random Allocation Simulation =================================
        traces = {}

        for col in self.tickers:
            traces[col] = go.Scatter(x=ef_df['Standard Deviation'] * 100,
                                     y=ef_df[col] * 100,
                                     name=col,
                                     # text=[round(c,2) for c in col],
                                     # mode='lines',
                                     # line=dict(width=0.5),
                                     stackgroup='one'
                                     )
        sim_data = list(traces.values())
        sim_fig = go.Figure(sim_data)
        sim_fig.update_traces(
            mode="lines",
            # hovertemplate=None
            hovertemplate=
            '<b>Allocation</b>: %{y:.2f}%'
            # '<b>Risk</b>: %{x:.2f}%'
            # hovertemplate="%{y}"
        )
        sim_fig.update_layout(
            xaxis_title="Standard Deviation",
            yaxis_title="Allocation",
            title="Random Allocation Simulation",
            titlefont=dict(size=36),
            legend_title='<b>Tickers</b>',
            showlegend=True,
            xaxis=dict(
                type='linear',
                ticksuffix='%'),
            yaxis=dict(
                type='linear',
                range=[1, 100],
                ticksuffix='%'),
            hovermode="x")
        SIMgraphJSON = json.dumps(sim_fig, cls=plotly.utils.PlotlyJSONEncoder)

        return TBLgraphJSON, EFgraphJSON, SIMgraphJSON, ALLOCgraphJSON

    # bring EF.py

    def portfolio_annualised_performance(self, weights, mean_returns,
                                         cov_matrix):
        """
        :param weights:
        :param mean_returns:
        :param cov_matrix:
        :return: expected volatility, expected return
        """
        # Expected Return
        returns = np.sum(mean_returns * weights) * 252
        # Expected Volatility
        # Denominator of the sharpe ratio
        # Use Linear Algebra here
        # transpose the weights
        # dot product of log_returns covariance multiplied by 252 with weights
        # sqrt of whole thing gives the expected volatility
        std = np.sqrt(
            np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(
            252)
        return std, returns

    def random_portfolios(self, num_portfolios, mean_returns, cov_matrix,
                          risk_free_rate, tickers):
        # results for vol, return, sharpe ratio
        results = np.zeros((3, num_portfolios))
        # allocation ratio
        weights_record = []
        for i in range(num_portfolios):
            # create random weights for number of tickers
            weights = np.random.random(len(tickers))
            # rebalance - normalization
            weights = weights / np.sum(weights)
            weights_record.append(weights)
            portfolio_std_dev, portfolio_return = self.portfolio_annualised_performance(
                weights, mean_returns, cov_matrix)
            # Standard Deviation
            results[0, i] = portfolio_std_dev
            # Expected Return
            results[1, i] = portfolio_return
            # Sharpe Ratio
            results[2, i] = (
                                    portfolio_return - risk_free_rate) / portfolio_std_dev

        weights_df = pd.DataFrame.from_records(weights_record, columns=tickers)
        result_df = pd.DataFrame.from_records(results.T,
                                              columns=['Standard Deviation',
                                                       'Expected Return',
                                                       'Sharpe Ratio'])
        portfolio_allocation_df = pd.concat([weights_df, result_df],
                                            axis=1).sort_values(
            by=['Expected Return'], ascending=False)
        return portfolio_allocation_df

    def neg_sharpe_ratio(self, weights, mean_returns, cov_matrix,
                         risk_free_rate):
        p_var, p_ret = self.portfolio_annualised_performance(weights,
                                                             mean_returns,
                                                             cov_matrix)
        return -(p_ret - risk_free_rate) / p_var

    def max_sharpe_ratio(self, mean_returns, cov_matrix, risk_free_rate):
        num_assets = len(mean_returns)
        args = (mean_returns, cov_matrix, risk_free_rate)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bound = (0.0, 1.0)
        bounds = tuple(bound for asset in range(num_assets))
        result = optimize.minimize(self.neg_sharpe_ratio,
                                   num_assets * [1. / num_assets, ],
                                   args=args,
                                   method='SLSQP', bounds=bounds,
                                   constraints=constraints,
                                   options={"disp": True})
        return result

    def portfolio_volatility(self, weights, mean_returns, cov_matrix):
        return self.portfolio_annualised_performance(weights, mean_returns,
                                                     cov_matrix)[
            0]

    def min_variance(self, mean_returns, cov_matrix):
        num_assets = len(mean_returns)
        args = (mean_returns, cov_matrix)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bound = (0.0, 1.0)
        bounds = tuple(bound for asset in range(num_assets))

        result = optimize.minimize(self.portfolio_volatility,
                                   num_assets * [1. / num_assets, ], args=args,
                                   method='SLSQP', bounds=bounds,
                                   constraints=constraints)

        return result

    def efficient_return(self, mean_returns, cov_matrix, target):
        num_assets = len(mean_returns)
        args = (mean_returns, cov_matrix)

        def portfolio_return(weights):
            return self.portfolio_annualised_performance(weights, mean_returns,
                                                         cov_matrix)[1]

        constraints = (
            {'type': 'eq', 'fun': lambda x: portfolio_return(x) - target},
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for asset in range(num_assets))
        result = optimize.minimize(self.portfolio_volatility,
                                   num_assets * [1. / num_assets, ], args=args,
                                   method='SLSQP', bounds=bounds,
                                   constraints=constraints)
        return result

    def efficient_frontier(self, mean_returns, cov_matrix, returns_range):
        efficients = []
        for ret in returns_range:
            efficients.append(
                self.efficient_return(mean_returns, cov_matrix, ret))
        return efficients

    def display_ef(self, mean_returns, cov_matrix, risk_free_rate,
                   num_portfolios,
                   returns, df, tickers):
        port_alloc_df = self.random_portfolios(num_portfolios, mean_returns,
                                               cov_matrix,
                                               risk_free_rate, tickers)

        max_sharpe = self.max_sharpe_ratio(mean_returns, cov_matrix,
                                           risk_free_rate)
        # expected volatility, expected return
        expected_volatility, expected_return = self.portfolio_annualised_performance(
            max_sharpe['x'],
            mean_returns,
            cov_matrix)  # weights,
        max_sharpe_allocation = pd.DataFrame(max_sharpe.x, index=df.columns,
                                             columns=['allocation'])
        max_sharpe_allocation.allocation = [round(i * 100, 2) for i in
                                            max_sharpe_allocation.allocation]
        max_sharpe_allocation = max_sharpe_allocation.T

        # Minimum volatility, minimum expected return
        min_vol = self.min_variance(mean_returns, cov_matrix)
        min_expected_volatility, min_expected_return = self.portfolio_annualised_performance(
            min_vol['x'],
            mean_returns,
            cov_matrix)
        min_vol_allocation = pd.DataFrame(min_vol.x, index=df.columns,
                                          columns=['allocation'])
        min_vol_allocation.allocation = [round(i * 100, 2) for i in
                                         min_vol_allocation.allocation]
        min_vol_allocation = min_vol_allocation.T

        annual_volatility = np.std(returns) * np.sqrt(252)
        annual_return = mean_returns * 252

        print("-" * 80)
        print("Maximum Sharpe Ratio Portfolio Allocation\n")
        print("Annualised Return:", expected_return)
        print("Annualised Volatility:", expected_volatility)
        print(max_sharpe_allocation)  # red star
        print("-" * 80)

        print("Minimum Volatility Portfolio Allocation\n")
        print("Annualised Return:", min_expected_return)
        print("Annualised Volatility:", min_expected_volatility)
        print(min_vol_allocation)  # green star
        print("-" * 80)
        print("Individual Stock Returns and Volatility\n")
        for i, txt in enumerate(df.columns):
            print(txt, ":", "annualised return", annual_return[i],
                  "| annualised volatility:", annual_volatility[i])
        print("-" * 80)

        frontier_y = np.linspace(min_expected_return, expected_return,
                                 100)  # This is frontier_y, expected return
        efficient_portfolios = self.efficient_frontier(mean_returns,
                                                       cov_matrix,
                                                       frontier_y)

        # fun is Volatility, x is Allocation, frontier_y=target is expected Return / sharpe ratio? ret / vol

        frontier_vol = [p['fun'] for p in efficient_portfolios]
        ef_alloc = [p['x'] for p in efficient_portfolios]
        ef_sr = frontier_y / np.array(frontier_vol)

        ef_alloc_df = pd.DataFrame.from_records(ef_alloc,
                                                columns=tickers)  # 10,000
        ef_vol_df = pd.DataFrame(frontier_vol,
                                 columns=['Standard Deviation'])  # 10,000
        ef_ret_df = pd.DataFrame(frontier_y,
                                 columns=['Expected Return'])  # 100
        ef_sr_df = pd.DataFrame(ef_sr, columns=['Sharpe Ratio'])  # 100

        ef_df = pd.concat([ef_alloc_df, ef_vol_df, ef_sr_df, ef_ret_df],
                          axis=1).sort_values(by=['Expected Return'])
        return annual_volatility, annual_return, expected_volatility, \
               expected_return, min_expected_volatility, min_expected_return, \
               max_sharpe, min_vol, frontier_vol, frontier_y, ef_df, \
               max_sharpe_allocation, min_vol_allocation

    def run_simulation(self, df):
        all_weights = np.zeros((self.num_portfolios, len(df.columns)))
        ret_arr = np.zeros(self.num_portfolios)
        vol_arr = np.zeros(self.num_portfolios)
        sharpe_arr = np.zeros(self.num_portfolios)

        for ind in range(self.num_portfolios):
            # Create Random Weights
            weights = np.array(np.random.random(len(self.tickers)))

            # Rebalance Weights
            weights = weights / np.sum(weights)

            # Save Weights
            all_weights[ind, :] = weights

            # Expected Return
            ret_arr[ind] = np.sum((df.pct_change().mean() * weights) * 252)

            # Expected Variance
            vol_arr[ind] = np.sqrt(
                np.dot(weights.T,
                       np.dot(df.pct_change().cov() * 252, weights)))

            # Sharpe Ratio
            sharpe_arr[ind] = ret_arr[ind] / vol_arr[ind]

        return vol_arr, ret_arr, sharpe_arr
