import unittest
from tests.test_base import BaseTestCase
from tests.utils.test_cleint import create_test_client
from tests.utils import auth_helpers

class TestFriendshipRouters(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client = create_test_client(db_session=self.db)
    
        

    def tearDown(self):
        return super().tearDown()
    
    #Utils
    def create_second_user(self) -> dict:
        response = self.client.post(
            "/auth/register",
            json={
                "email": "friend@example.com",
                "password": "password",
                "password_repeat": "password",
                "first_name": "Friend",
                "last_name": "User",
                "birth_date": "2000-01-01"
            }
        )
        return response.json()
    
    def get_user_token(self, user: dict) -> str:
        login_user = auth_helpers.login_user(
            self.client,
            email=user["email"],
            password="password"
        )
        
        token = login_user.json()

        return token["access_token"]
    

    #Create friend request
    def test_create_friend_request_success(self): #success
        header = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()

        response = self.client.post(
            url="/friendships/",
            json={"addressee_id": second_user['id']},
            headers=auth_helpers.auth_header(token=header)
        )
        
        self.assertEqual(response.status_code, 201)

    
    def test_create_friend_request_already_exists(self): #already exists
        header = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()

        self.client.post(
          "/friendships/",
          json={"addressee_id": second_user['id']},
          headers=auth_helpers.auth_header(token=header)
        )
        
        response = self.client.post(
          "/friendships/",
          json={"addressee_id": second_user['id']},
          headers=auth_helpers.auth_header(token=header)
        )

        self.assertEqual(response.status_code, 409)

    #Accept friend request
    def test_accept_friend_request(self): #success
        token1 = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()

        create_friendship = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token=token1)
        )
        
        self.assertEqual(create_friendship.status_code, 201)

        friendship_id = create_friendship.json()["id"]

        token2 = self.get_user_token(second_user)

        response = self.client.patch(
            f"/friendships/{friendship_id}/accept",
            headers=auth_helpers.auth_header(token=token2)
        )

        self.assertEqual(response.status_code, 200)

    
    def test_accept_friend_request_not_found(self): #not found
        token = auth_helpers.get_access_token(self.client)

        response = self.client.patch(
            "/friendships/99/accept",
            headers=auth_helpers.auth_header(token=token)
        )

        self.assertEqual(response.status_code, 404)

    
    def test_accept_friend_request_already_accepted(self): #alreade accepted
        token1 = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()

        create_friendship = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token=token1)
        )
        
        self.assertEqual(create_friendship.status_code, 201)

        friendship_id = create_friendship.json()["id"]

        token2 = self.get_user_token(second_user)

        accept_friend_request = self.client.patch(
            f"/friendships/{friendship_id}/accept",
            headers=auth_helpers.auth_header(token=token2)
        )

        response = self.client.patch(
            f"/friendships/{friendship_id}/accept",
            headers=auth_helpers.auth_header(token=token2)
        )

        self.assertEqual(response.status_code, 409)


    def test_accept_friend_request_already_rejected(self): #already rejected
        token1 = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()

        create_friendship = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token=token1)
        )
        
        self.assertEqual(create_friendship.status_code, 201)

        friendship_id = create_friendship.json()["id"]

        token2 = self.get_user_token(second_user)

        reject_friend_request = self.client.patch(
            f"/friendships/{friendship_id}/reject",
            headers=auth_helpers.auth_header(token=token2)
        )

        response = self.client.patch(
            f"/friendships/{friendship_id}/accept",
            headers=auth_helpers.auth_header(token=token2)
        )

        self.assertEqual(response.status_code, 409)


    def test_accept_friend_request_permission_denied(self): #permission denied
        token1 = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()

        friendship_id = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token=token1)
        ).json()["id"]


        denied_user = auth_helpers.register_user(
            self.client,
            email="DeniedUser@example.com",
            password="password"
        ).json()

        token_denied_user = self.get_user_token(denied_user)

        response = self.client.patch(
            f"/friendships/{friendship_id}/accept",
            headers=auth_helpers.auth_header(token_denied_user)
        )
        
        self.assertEqual(response.status_code, 403)
    

    #Reject friend request
    def test_reject_friend_request_success(self): #success
        token1 = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()
        
        token2 = self.get_user_token(second_user)

        friendship_id = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token=token1)
        ).json()["id"]

        response = self.client.patch(
            f"/friendships/{friendship_id}/reject",
            headers=auth_helpers.auth_header(token=token2)
        )

        self.assertEqual(response.status_code, 200)
    

    def test_reject_friend_request_already_rejected(self): #already rejected
        token1 = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()

        token2 = self.get_user_token(second_user)

        friendship_id = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token=token1)
        ).json()["id"]

        reject_friendship_request = self.client.patch(
            f"/friendships/{friendship_id}/reject",
            headers=auth_helpers.auth_header(token=token2)
        )

        response = self.client.patch(
            f"/friendships/{friendship_id}/reject",
            headers=auth_helpers.auth_header(token=token2)
        )

        self.assertEqual(response.status_code, 409)
    

    def test_reject_friend_request_already_accepted(self): #already accepted
        token1 = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()

        token2 = self.get_user_token(second_user)

        friendship_id = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token=token1)
        ).json()["id"]

        accept_friendship_request = self.client.patch(
            f"/friendships/{friendship_id}/accept",
            headers=auth_helpers.auth_header(token=token2)
        )

        response = self.client.patch(
            f"/friendships/{friendship_id}/reject",
            headers=auth_helpers.auth_header(token=token2)
        )

        self.assertEqual(response.status_code, 409)


    def test_reject_friend_request_not_found(self): #not found
        token = auth_helpers.get_access_token(self.client)

        response = self.client.patch(
            "/friendships/123/reject",
            headers=auth_helpers.auth_header(token)
        )

        self.assertEqual(response.status_code, 404)


    def test_reject_friend_request_permission_denied(self): #permission denied
        token1 = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()

        friendship_id = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token1)
        ).json()["id"]

        denied_user = auth_helpers.register_user(
            self.client,
            email="DeniedUser@example.com",
            password="password"
        ).json()

        token_denied_user = self.get_user_token(denied_user)

        response = self.client.patch(
            f"/friendships/{friendship_id}/reject",
            headers=auth_helpers.auth_header(token_denied_user)
        )

        self.assertEqual(response.status_code, 403)
    

    #Remove friendship
    def test_remove_friendship_success(self): #success
        token1 = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()

        token2 = self.get_user_token(second_user)

        friendship_id = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token=token1)
        ).json()["id"]

        accept_friendship = self.client.patch(
            f"/friendships/{friendship_id}/accept",
            headers=auth_helpers.auth_header(token2)
        )

        response = self.client.delete(
            f"/friendships/{friendship_id}",
            headers=auth_helpers.auth_header(token1)
        )

        self.assertEqual(response.status_code, 204)

    
    def test_remove_friendship_not_found(self): #not found
        token = auth_helpers.get_access_token(self.client)

        response = self.client.delete(
            "/friendships/123",
            headers=auth_helpers.auth_header(token=token)
        )

        self.assertEqual(response.status_code, 404)


    def test_remove_friendship_permission_denied(self): #permission denied
        token1 = auth_helpers.get_access_token(self.client)
        second_user = self.create_second_user()

        token2 = self.get_user_token(second_user)

        friendship_id = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token1)
        ).json()["id"]

        denied_user = auth_helpers.register_user(
            self.client,
            email="DeniedUser@example.com",
            password="password"
        ).json()

        denied_user_token = self.get_user_token(denied_user)

        response = self.client.delete(
            f"/friendships/{friendship_id}",
            headers=auth_helpers.auth_header(denied_user_token)
        )

        self.assertEqual(response.status_code, 403)


    #Get requests
    def test_get_requests_success(self): #success
        second_user = self.create_second_user()
        third_user = auth_helpers.register_user(
            self.client,
            email="ThirdUser@example.com",
            password="password"
        ).json()

        token1 = auth_helpers.get_access_token(self.client)
        token2 = self.get_user_token(second_user)
        token3 = self.get_user_token(third_user)

        friendship1 = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token1)
        )

        friendship2 = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token3)
        )

        friendship3 = self.client.post(
            "/friendships/",
            json={"addressee_id": third_user["id"]},
            headers=auth_helpers.auth_header(token1)
        )

        response = self.client.get(
            "/friendships/requests",
            headers=auth_helpers.auth_header(token=token2)
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 2)


    #Get friends
    def test_get_friends_success(self):
        first_user = self.client.post(
            "/auth/register",
            json={
                "email": "test1@example.com",
                "password": "password",
                "password_repeat": "password",
                "first_name": "Test1",
                "last_name": "User1",
                "birth_date": "2000-01-01"
            }
        ).json()

        second_user = self.create_second_user()

        third_user = self.client.post(
            "/auth/register",
            json={
                "email": "test3@example.com",
                "password": "password",
                "password_repeat": "password",
                "first_name": "Test3",
                "last_name": "User3",
                "birth_date": "2000-01-01"
            }
        ).json()

        token1 = self.get_user_token(first_user)
        token2 = self.get_user_token(second_user)
        token3 = self.get_user_token(third_user)

        friendship_id_1 = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token1)
        ).json()["id"]

        friendship_id_2 = self.client.post(
            "/friendships/",
            json={"addressee_id": second_user["id"]},
            headers=auth_helpers.auth_header(token3)
        ).json()["id"]

        accept_friendship1 = self.client.patch(
            f"/friendships/{friendship_id_1}/accept",
            headers=auth_helpers.auth_header(token2)
        )

        reject_friendship2 = self.client.patch(
            f"/friendships/{friendship_id_2}/reject",
            headers=auth_helpers.auth_header(token2)
        )

        response = self.client.get(
            "/friendships/friends",
            headers=auth_helpers.auth_header(token2)
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertEqual(len(response.json()), 1)






if __name__ == "main":
    unittest.main()