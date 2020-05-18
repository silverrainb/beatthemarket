from flask import url_for

from lib.tests import assert_status_with_message, ViewTestMixin


class TestNews(ViewTestMixin):

    def test_show(self):
        response = self.client.get(url_for('news.show'))
        assert_status_with_message(302, response, 'news')

    # def test_redirection_followed(self):
    #     self.login()
    #     if ticker doesn't exists:
    #         response = self.client.get(url_for('news.show'),
    #                                    follow_redirects=False)
    #         assert_status_with_message(200, response, 'MarketNews is available when holding records are available.')
    #     else:
    #         response = self.client.get(url_for('news.show'), follow_redirects=False)
    #         import pytest
    #         pytest.set_trace()
    #         assert_status_with_message(200, response, 'Market News')

    def test_redirection_followed_no_login(self):
        response = self.client.get(url_for('news.show'), follow_redirects=True)
        assert_status_with_message(200, response, 'Please log in to access this page')
