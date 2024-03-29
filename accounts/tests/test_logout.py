from test.pages.common import HomePage, LogOut
from test.utils.helpers import (
    client_login,
    client_logout,
    create_member,
    response_user_logged_in,
)
from typing import *

from django.test import TestCase

# test user login credentials
TEST_USER_LOGIN_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="testuser",
    password="testpassword",
)


class TestLogout(TestCase):
    def setUp(self) -> None:
        create_member(**TEST_USER_LOGIN_CREDENTIALS)
        return super().setUp()

    def test_logout_redirects_anonymous_user_to_home_page(self):
        response = self.client.post(LogOut.get_url())
        self.assertRedirects(
            response,
            HomePage.get_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_logout_with_logged_in_user(self):
        response = client_login(self.client, TEST_USER_LOGIN_CREDENTIALS)
        self.assertTrue(response_user_logged_in(response))

        response = client_logout(self.client, follow=True)
        self.assertFalse(response_user_logged_in(response))

    def test_logout_redirects_to_homepage(self):
        response = client_login(self.client, TEST_USER_LOGIN_CREDENTIALS)
        self.assertTrue(response_user_logged_in(response))

        response = client_logout(self.client, follow=False)
        self.assertRedirects(
            response,
            HomePage.get_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
