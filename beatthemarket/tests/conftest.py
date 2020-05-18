import pytest

from config import settings

from beatthemarket.blueprints.user.models import User
from beatthemarket.blueprints.portfolio.models import MarketSummary, \
    CurrentPrice, Holding
from beatthemarket.app import create_app
from beatthemarket.extensions import db as _db


@pytest.yield_fixture(scope='session')
def app():
    """
    Setup our flask test app, this only gets executed once.

    :return: Flask app
    """
    db_uri = '{0}_test'.format(settings.SQLALCHEMY_DATABASE_URI)
    params = {
        'DEBUG': False,
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': db_uri
    }

    _app = create_app(settings_override=params)

    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope='function')
def client(app):
    """
    Setup an app client, this gets executed for each test function.

    :param app: Pytest fixture
    :return: Flask app client
    """
    # track of cookies
    yield app.test_client()


# @pytest.fixture(scope='module') # session
# def db(app):
#     """
#     Setup our database, this only gets executed once per session.
#
#     :param app: Pytest fixture
#     :return: SQLAlchemy database session
#     """
#     _db.drop_all()
#     _db.create_all()
#
#     # Create a single user because a lot of tests do not mutate this user.
#     # It will result in faster tests.
#     # params = {
#     #     'role': 'admin',
#     #     'email': 'admin@local.host',
#     #     'password': 'password'
#     # }
#
#     admin = User(email='admin@local.host', password='password')
#
#     _db.session.add(admin)
#     _db.session.commit()
#     yield _db
#     db.drop_all()
#     # pytest.set_trace()
#     # return _db


@pytest.fixture(scope='module')
def db(app):
    _db.drop_all()
    _db.create_all()

    user1 = User(email='admin@local.host',
                 password='password')
    _db.session.add(user1)
    _db.session.commit()

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
    current_prices = {'MSFT': 183.39}
    market_summ = {"MSFT": {"Previous Close": "180.76", "Open": "182.08",
                            "Bid": "183.38 x 1000", "Ask": "183.36 x 1200",
                            "Day''s Range": "181.64 - 183.90",
                            "52 Week Range": "119.01 - 190.70",
                            "Volume": "16174754",
                            "Avg. Volume": "56224046", "Market Cap": "1.391T",
                            "Beta (5Y Monthly)": "0.95",
                            "PE Ratio (TTM)": "30.56",
                            "EPS (TTM)": "6.00",
                            "Earnings Date": "Jul 16, 2020 - Jul 20, 2020",
                            "Forward Dividend & Yield": "2.04 (1.17%)",
                            "Ex-Dividend Date": "May 20, 2020",
                            "1y Target Est": "193.94",
                            "Current Price": 183.42}}
    curr = CurrentPrice(data=current_prices)

    holds = Holding(**holding)
    _db.session.add(holds)
    _db.session.commit()

    _db.session.add(curr)
    _db.session.commit()

    market_summ = MarketSummary(data=market_summ)
    _db.session.add(market_summ)
    _db.session.commit()

    yield _db  # this is where the testing happens!

    _db.drop_all()


# @pytest.yield_fixture(scope='function')
# def db(app):
#     # app is an instance of a flask app, _db a SQLAlchemy DB
#     _db.app = app
#     with app.app_context():
#         _db.create_all()
#
#     yield _db
#
#     # Explicitly close DB connection
#     _db.session.close()
#     _db.drop_all()


@pytest.yield_fixture(scope='function')
def session(db):
    """
    Allow very fast tests by using rollbacks and nested sessions. This does
    require that your database supports SQL savepoints, and Postgres does.

    Read more about this at:
    http://stackoverflow.com/a/26624146

    :param db: Pytest fixture
    :return: None
    """
    db.session.begin_nested()

    yield db.session

    db.session.rollback()


@pytest.fixture(scope='session')
def token(db):
    """
    Serialize a JWS token.

    :param db: Pytest fixture
    :return: JWS token
    """
    user = User.find_by_identity('admin@local.host')
    return user.serialize_token()


@pytest.fixture(scope='function')
def users(db):
    """
    Create user fixtures. They reset per test.

    :param db: Pytest fixture
    :return: SQLAlchemy database session
    """
    db.session.query(User).delete()

    users = [
        {
            'role': 'admin',
            'email': 'admin@local.host',
            'password': 'password'
        },
        {
            'active': False,
            'email': 'disabled@local.host',
            'password': 'password'
        }
    ]

    for user in users:
        db.session.add(User(**user))

    db.session.commit()

    return db
