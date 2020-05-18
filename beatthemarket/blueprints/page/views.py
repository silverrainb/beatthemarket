from flask import Blueprint, redirect, url_for

page = Blueprint('page', __name__)


@page.route('/')
def home():
    return redirect(url_for('user.register'))
