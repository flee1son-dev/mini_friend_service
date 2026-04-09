import unittest

from tests.test_base import BaseTestCase
from tests.utils.test_cleint import create_test_client
from tests.utils import auth_helpers

class TestAuthRouters(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client = create_test_client(db_session=self.db)

    def tearDown(self):
        super().tearDown()
    

    #Register user
    def test_register_success(self): #success
        response = auth_helpers.register_user(self.client)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "test@example.com")
    

    def test_register_duplicate_email(self): #email already exists
        auth_helpers.register_user(self.client)
        response = auth_helpers.register_user(self.client)

        self.assertEqual(response.status_code, 409)

    
    def test_register_password_mismatch(self): #password mismatch
        response = self.client.post(url="/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "password_repeat": "123password",
            "first_name": "Test",
            "last_name": "User",
            "birth_date": "2000-01-01"
        })

        self.assertEqual(response.status_code, 422)

    
    #Login user
    def test_login_success(self): #success
        auth_helpers.register_user(self.client)
        response = auth_helpers.login_user(self.client)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertIn("refresh_token", response.cookies)

    
    def test_login_invalid_credentials(self): #invalid credentials
        response = auth_helpers.login_user(self.client)

        self.assertEqual(response.status_code, 401)


    #Refresh login
    def test_refresh_success(self): #success
        auth_helpers.register_user(self.client)
        login_response = auth_helpers.login_user(self.client)
        
        self.client.cookies.set(
        "refresh_token",
        login_response.cookies.get("refresh_token")
        )

        response = self.client.post("/auth/refresh")

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())


    def test_refresh_without_cookie(self): #Wothiout cookie
        response = self.client.post(url="/auth/refresh")

        self.assertEqual(response.status_code, 401) 

    #Logout
    def test_logout_success(self):  #success
        auth_helpers.register_user(self.client)
        login_response = auth_helpers.login_user(self.client)

        access_token = login_response.json()["access_token"]

        response = self.client.post(
            "/auth/logout",
            cookies=login_response.cookies,
            headers=auth_helpers.auth_header(access_token)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "Successfully logged out")


    def test_logout_invalid_token(self): #logout with invalid token
        response = self.client.post(
            "/auth/logout",
            headers=auth_helpers.auth_header("invalid token")
        )

        self.assertEqual(response.status_code, 401)

        
if __name__ == "__main__":
    unittest.main