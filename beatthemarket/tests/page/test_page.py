from flask import url_for

from lib.tests import assert_status_with_message, ViewTestMixin


class TestPage(ViewTestMixin):
    def test_home_page_no_login(self):
        """ Home page should respond with a success 200. """
        response = self.client.get(url_for('user.register'))
        assert_status_with_message(200, response, 'Sign up today')

    def test_home_page_login(self):
        """ Home page should respond with a success 200. """
        self.login()
        response = self.client.get(url_for('user.register'))
        assert_status_with_message(302, response, "Redirecting...")

    def test_404_page(self):
        """ 404 errors should show the custom 404 page. """
        response = self.client.get('/testing404page')
        assert str(response.data).find('Page Not Found') != -1
