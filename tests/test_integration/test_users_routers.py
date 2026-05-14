import unittest
from tests.test_base import BaseTestCase
from tests.utils.test_cleint import create_test_client
from tests.utils import auth_helpers


class TestUsersRouters(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client = create_test_client(db_session=self.db)

    def tearDown(self):
        return super().tearDown()

    #Get all users
    def test_get_all_users(self): #success
        headers = auth_helpers.get_access_token(self.client)

        response = self.client.get(
            "/users",
            headers=auth_helpers.auth_header(headers)
        )

        self.assertEqual(response.status_code, 200)

    
    #Get me
    def test_get_me_success(self): #success
        headers = auth_helpers.get_access_token(self.client)

        response = self.client.get(
            "/users/me",
            headers=auth_helpers.auth_header(headers),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.json())

    def test_get_me_unauthorized(self): #unauthorized
        response = self.client.get("/users/me")

        self.assertEqual(response.status_code, 401)


    #Update me
    def test_update_me_success(self): #success
        headers = auth_helpers.get_access_token(self.client)

        response = self.client.put(
            "/users/me/update",
            json={
                "first_name": "UpdatedName",
                "last_name": "UpdatedLName",
                "email": "UpdatedEmail@example.com",
                "password": "123123123",
                "password_repeat": "123123123"
            },
            headers=auth_helpers.auth_header(headers)
        )

        self.assertEqual(response.status_code, 200)

    
    def test_update_me_password_mismatch(self): #password mismatch
        headers = auth_helpers.get_access_token(self.client)

        response = self.client.put(
            "/users/me/update",
            json={
                "password": "Hello",
                "password_repeat": "World"
            },
            headers=auth_helpers.auth_header(headers)
        )

        self.assertEqual(response.status_code, 422)

    
    def test_update_me_email_exists(self): #email already exists
        headers = auth_helpers.get_access_token(self.client)

        self.client.post( #test user
            "/auth/register",
            json={
                "email": "test2@example.com",
                "password": "password",
                "password_repeat": "password",
                "first_name": "Test2",
                "last_name": "User2",
                "birth_date": "2000-01-01"
            }
        )

        response = self.client.put(
            "/users/me/update",
            json={
                "email": "test2@example.com"
            },
            headers=auth_helpers.auth_header(headers)
        )

        self.assertEqual(response.status_code, 409)

    
    #Get users by first name
    def test_get_users_by_fname(self): #success
        headers = auth_helpers.get_access_token(self.client)

        self.client.post( #test user
            "/auth/register",
            json={
                "email": "test2@example.com",
            "password": "password",
            "password_repeat": "password",
            "first_name": "Test2",
            "last_name": "User2",
            "birth_date": "2000-01-01"
            }
        )

        self.client.post( #test user
            "/auth/register",
            json={
                "email": "test3@example.com",
                "password": "password",
                "password_repeat": "password",
                "first_name": "Test2",
                "last_name": "User2",
                "birth_date": "2000-01-01"
            }
        )

        self.client.post( #test user
            "/auth/register",
            json={
                "email": "test4@example.com",
                "password": "password",
                "password_repeat": "password",
                "first_name": "Miss",
                "last_name": "User2",
                "birth_date": "2000-01-01"
            }
        )

        response = self.client.get(
            "/users/search?first_name=Test2",
            headers=auth_helpers.auth_header(headers)
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 2)


    #Get user
    def test_get_user_success(self): #success
        headers = auth_helpers.get_access_token(self.client)

        me = self.client.get(
            "/users/me",
            headers=auth_helpers.auth_header(headers)
        ).json()

        response = self.client.get(
            f"/users/{me['id']}",
            headers=auth_helpers.auth_header(headers)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], me["id"])

    
    def test_get_user_not_found(self): #user not found
        headers = auth_helpers.get_access_token(self.client)

        response = self.client.get(
            "/users/999",
            headers=auth_helpers.auth_header(headers)
        )

        self.assertEqual(response.status_code, 404)

    
    #Delete user
    def test_delete_user(self):
        headers = auth_helpers.get_access_token(self.client)

        response = self.client.put(
            "/users/me/delete",
            json={"is_active": False},
            headers=auth_helpers.auth_header(headers)
        )

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
