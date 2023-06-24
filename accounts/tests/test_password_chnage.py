from typing import *

from django.test import TestCase
from django.test.client import Client

from tests.pages.common import (HomePage, LogIn, LogOut, PasswordChange,
                                PasswordChangeDone)
from tests.utils.helpers import (client_login, client_logout, create_member,
                                    page_title_in_response)

OLD_PASSWORD: Final[str] = "old_password"
NEW_PASSWORD: Final[str] = "new_password"

MEMBER_CREDENTIALS: Final[Dict[str, str]] = dict(
    username="testuser",
    password=OLD_PASSWORD,
)


class TestPasswordChange(TestCase):
    def setUp(self) -> None:
        create_member(**MEMBER_CREDENTIALS)
        
        self.client: Client = Client()
        client_login(self.client, MEMBER_CREDENTIALS)
        
        return super().setUp()

    def tearDown(self) -> None:
        client_logout(self.client)
        return super().tearDown()
    
    def test_password_change_rendering(self):
        response = self.client.get(PasswordChange.url)
        self.assertTemplateUsed(response, PasswordChange.template_name)
        self.assertTrue(page_title_in_response(PasswordChange, response))
    
    def test_password_change_form_old_password_required(self):
        response = self.client.post(
            PasswordChange.url,
            dict(
                new_password1= NEW_PASSWORD,
                new_password2= NEW_PASSWORD,
            )
        )
        
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["old_password"], ["This field is required."])
        
    def test_password_change_form_wrong_old_password(self):
        response = self.client.post(
            PasswordChange.url,
            dict(
                old_password="wrong_password",
                new_password1= NEW_PASSWORD,
                new_password2= NEW_PASSWORD,
            )
        )
        
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["old_password"], ["Your old password was entered incorrectly. Please enter it again."])
        
    def test_password_change_form_new_password_mismatch(self):
        response = self.client.post(
            PasswordChange.url,
            dict(
                old_password=OLD_PASSWORD,
                new_password1= "wrong_password",
                new_password2= NEW_PASSWORD,
            )
        )
        
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["new_password2"], ["The two password fields didn’t match."])
        
        
    
    def test_password_change_redirects_anonymous_user(self):
        client = Client()
        response = client.get(PasswordChange.url, follow=False)
        self.assertEqual(response.status_code, 302)
    
    def test_password_change_sequence(self):
        response = self.client.post(PasswordChange.url, {
                "old_password": OLD_PASSWORD,
                "new_password1": NEW_PASSWORD,
                "new_password2": NEW_PASSWORD,
            }
        )
        self.assertRedirects(response, PasswordChangeDone.url)

        response = client_logout(self.client)
        self.assertIsNone(self.client.session.session_key)
        
        response = client_login(self.client, dict(
                username=MEMBER_CREDENTIALS["username"],
                password=NEW_PASSWORD,
                follow=False,
            )
        )
        self.assertRedirects(response, HomePage.url)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertIsNotNone(self.client.session.session_key)
