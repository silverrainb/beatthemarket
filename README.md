# Beat the Market

[Beatthemarket](https://beatthemarket.herokuapp.com/) is an application that constructs an optimal asset portfolio. Users can add their holding records and view their P&L. Investment recommendation which uses a machine-learning algorithm provides predictive insights to enable and support smart investment decisions. Currently, te available features are {Bookkeeping stock holdings, Monitoring P&L, Portfolio allocation recommendation, Market news}.


# Features
## Authentication
Users need to create an account and cannot see others' portfolios. The web application features are only accessible after registration.
## Background workers
The app is kept responsive and the required data is up-to-date according to users' inputs.
## Holdings
Users can bookkeep their stock holdings.
## P&L
Users can view their P&L in treemap as well as data table which provides search and sort options.
## Insights
Insights provide [Efficient Frointier](https://www.investopedia.com/terms/e/efficientfrontier.asp) based on the user's current portfolio allocation. The efficient frontier is the set of optimal portfolios that offers the highest expected return for a defined level of risk or the lowest risk for a given level of expected return. Portfolios that lie below the efficient frontier are sub-optimal because they do not provide enough return for the level of risk. Portfolios that cluster to the right of the efficient frontier are also sub-optimal because they have a higher level of risk for the defined rate of return.

[Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp) is a measure for calculating risk-adjusted return and this is the industry standard for such calculation developed by Nobel laureate William F Sharpe. The formula for `SR = Mean Return / Std.Dev.`

[Risk-Free Return](https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=billRatesYear&year=2020) is the return that one would receive by investing their money in a bank saving account or buying treasury bonds that are essentially `risk-free`. In beatthemarket, we use `1.52%` which is 52 weeks bank discount rate of 2020-01-02 according to the U.S. Department of the Treasury.

Monte Carlo Simulation runs 15,000 times of random allocation in beatthemarket and checks which allocation shows the best Sharpe Ratio. Then to calculate optimal Sharpe Ratio, we create an optimizer that attempts to minimize the negative of Sharpe Ratio to maximize the Sharpe Ratio. `Insights` implements Scipy's built-in optimization algorithms to calculate the optimal weight allocation for users' portfolios.

The Efficient Frontier plot shows 
* Efficient Frontier Line and simulated allocation
* Current invested stocks position
* Maximum Sharpe Ratio portfolio position
* Minimum volatility portfolio position

Random Allocation Simulation plot shows the allocation weights according to the simulation dots displayed in the Efficient Frontier plot.

Portfolio Comparison table shows Expected Return, Expected Volatility, and Sharpe Ratio of the current portfolio in comparison of Maximum SR Portfolio and Minimum Volatility Portfolio.

Finally, Allocation Weights table shows the break down of portfolio allocation to achieve maximum SR or minimum Volatility.

## News

IEX API provides current news according to the tickers users own in their holding records. If a user has no records in holdings, users will be advised to add recordings and redirected them to the holdings page.


# User Flow(story)

![beatthemarket_userflow.gif](img/beatthemarket_userflow.gif)

Users can sign up on the beatthemarket. The welcome page suggests the user creates an immutable username. Users can click Holdings and add inputs of the stock portfolio. Then on the P&L page, user can view their current portfolio in the treemap plot as well as in the data table. On Insights pages which show user suggestions of a rebalanced portfolio based on the current market situation, the user may take an action on their brokerage platform. Coming back the next day to beatthemarket, users can log in to check their PL, read news about their stock.

# Technology Stack used to create Beatthemarket
* Python
    * Flask: 
        - Incorporated Flask factory pattern to set up the project.
        - Flask login_manager and bcrypt are used for user authentication.
        - WTForms used for form validation.
        - APScheduler is running background work for data collection
        - SQLAlchemy to manage a database in flask application.
    * Jinja:
        - Using server rendered templates with sprinkles of JavaScript
    * Celery:
        - Running background work to send reset password emails and collecting data.
    * APScheduler
        - Schedule code to be executed periodically to update the database.
    * BS4
    * Data Science: Scipy, Pandas, Numpy, Plotly
    * pytest
    * Click: Simple cli implementation with basics commands
        
* JavaScript
    * jQuery , Bootstrap for responsiveness, styling and to handle inter-activities.
    * Plotly, D3 to display and render plots.

* Database
    * PostgreSQL
    * Redis

* Infrastructure/Deployment
    * Docker

# Data Source
## API
* [IEX Cloud](https://cloud.iexapis.com)
* [Pandas Datareader](https://pandas-datareader.readthedocs.io/en/latest/)

## Web Scraping
* [Yahoo Finance](https://finance.yahoo.com/)
* [S&P 500 Tickers](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)
* [NASDAQ 100 Tickers](https://en.wikipedia.org/wiki/NASDAQ-100)

## Risk-Free Rate
* [Risk-free rate comes from Treasury](https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=billRatesYear&year=2020)


# How to initiate the application
## Docker
* To build docker and run:
    * create **.env** file to include:
        ```
        export MAIL_USERNAME = email address
        export MAIL_PASSWORD = password
        export API_BASE_URL = api base url
        export MY_API_KEY = api key
        export FLASK_SECRET_KEY = add flask secret key
        ```
        - [Get email credentials](myaccount.google.com/apppasswords)
        - Mail credentials are used for a password reset
        - API credentials are used for fetching news
    * Uncomment `docker` part and comment out related vars.
    * build the app `$ docker-compose up --build`
    * initiate db `$ docker-compose exec website beatthemarket db reset --with-testdb`
    * access at `localhost:8000`
    
## Local for debug
* celery is using redis wrapped in docker.
* SQLAlchemy config accordingly.
* `$ export FLASK_APP=run`
* `$ flask run`
* `$ beatthemarket db init/reset/seed`
## Wrap-up
* stop the app `docker-compose stop`
* to restart `docker-compose up`
* To remove everything: `docker-compose rm -f`
* Remove all dangling dockers: `docker rmi -f $(docker images -qf dangling=true)`

# Test
* Run Tests: `docker-compose exec website py.test --timeout=60 beatthemarket/tests`
* Coverage Test: `docker-compose exec website py.test --cov-report term-missing --cov beatthemarket`

# Deployment
* [Write heroku.yml](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml)
* [Heroku logging](https://devcenter.heroku.com/articles/logging#view-logs)
* setup database add-ons
    - `$ heroku addons:create heroku-postgresql:hobby-dev`
    - `$ heroku addons:create heroku-redis:hobby-dev`
* enable dynos on heroku resources for web and celery
* initialize DB
    * `$ heroku pg:psql`
        - list all `\l`
        - get out `\q`
        - seed.py file to run in heroku `heroku run python seed.py`
        OR...
    * on heroku app dashboard, more > run console > bash > `beatthemarket db init`

# Stretch Goal
* Merge Price Prediction Feature along with visualization

