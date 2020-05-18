from lib.util_sqlalchemy import ResourceMixin
from beatthemarket.extensions import db
from sqlalchemy.dialects.postgresql import JSONB


class Holding(ResourceMixin, db.Model):
    __tablename__ = 'holdings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)
    type = db.Column(db.Text, nullable=False)
    ticker = db.Column(db.String(5), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    rpl = db.Column(db.Float, nullable=True)
    total_spending = db.Column(db.Float, nullable=True)
    date = db.Column(db.DateTime, nullable=False)

    users = db.relationship('User', backref='holdings')

    def __init__(self, **kwargs):
        super(Holding, self).__init__(**kwargs)

    @classmethod
    def initialize_update_market_data(cls):
        """
        Updates market data in the background.
        """
        # This prevents circular imports.
        from beatthemarket.blueprints.portfolio.tasks import (
            update_market_data)
        update_market_data.delay()

        return "Celery Work Success"

    @property
    def __repr__(self):
        return f"<Holding {self.user_id} {self.type} {self.ticker} {self.quantity} {self.price} {self.date} >"


class MarketSummary(ResourceMixin, db.Model):
    __tablename__ = 'market_summ'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(JSONB, nullable=False)

    def __init__(self, **kwargs):
        super(MarketSummary, self).__init__(**kwargs)


class CurrentPrice(ResourceMixin, db.Model):
    __tablename__ = 'current_prices'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(JSONB, nullable=False)

    def __init__(self, **kwargs):
        super(CurrentPrice, self).__init__(**kwargs)


class PL(ResourceMixin, db.Model):
    __tablename__ = 'pl'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)
    data = db.Column(JSONB, nullable=False)

    users = db.relationship('User', backref='pl')

    def __init__(self, **kwargs):
        super(PL, self).__init__(**kwargs)


class Insight(ResourceMixin, db.Model):
    __tablename__ = 'insights'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticker = db.Column(db.String, nullable=False)
    data = db.Column(JSONB, nullable=False)

    def __init__(self, **kwargs):
        super(Insight, self).__init__(**kwargs)
