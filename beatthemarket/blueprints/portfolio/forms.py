from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, StringField, \
    IntegerField, FloatField, DateField
from wtforms.validators import InputRequired, DataRequired, Length


class AddHoldingsForm(FlaskForm):
    next = HiddenField()
    type = SelectField(
        "Type",
        choices=[("buy", "Buy"), ("sell", "Sell")]
    )

    ticker = StringField(
        "Ticker",
        validators=[InputRequired(),
                    DataRequired(),
                    Length(1, 5)]
    )

    quantity = IntegerField(
        "Quantity",
        validators=[InputRequired(),
                    DataRequired()]
    )

    price = FloatField(
        "Price Per Share",
        validators=[InputRequired(),
                    DataRequired()]
    )

    date = DateField(
        "Date",
        validators=[InputRequired(),
                    DataRequired()], format='%Y-%m-%d'
    )
