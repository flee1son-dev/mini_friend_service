import unittest

from tests.test_base import BaseTestCase
from backend.modules.friendships import services as friendships_services
from backend.modules.friendships import models as FriendshipModels, schemas as FriendshipSchemas
from backend.modules.users import models as UserModels
from backend.core import security, exceptions
from datetime import date


class TestFriendshipService(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user1 = self.user1 = UserModels.User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            birth_date=date(year=2000, month=1, day=1),
            password=security.hash_password("password123"),
            is_active=True
        )

        self.user2 = UserModels.User(
            email="test2@example.com",
            first_name="Test2",
            last_name="User2",
            birth_date=date(year=2002, month=4, day=4),
            password=security.hash_password("password123"),
            is_active=True
        )

        self.user3 = UserModels.User(
            email="test3@example.com",
            first_name="Test3",
            last_name="User3",
            birth_date=date(year=2007, month=12, day=21),
            password=security.hash_password("password123"),
            is_active=True
        )

        self.user4 = UserModels.User(
            email="test4@example.com",
            first_name="Test4",
            last_name="User4",
            birth_date=date(year=1991, month=5, day=4),
            password=security.hash_password("password123"),
            is_active=True
        )

        self.friendship1 = FriendshipModels.Friendship(
            status=FriendshipModels.FriendshipStatus.accepted,
            requester= self.user1,
            addressee= self.user2
        )

        self.friendship2 = FriendshipModels.Friendship(
            status=FriendshipModels.FriendshipStatus.accepted,
            requester= self.user1,
            addressee= self.user3
        )

        self.friendship3 = FriendshipModels.Friendship(
            status=FriendshipModels.FriendshipStatus.pending,
            requester= self.user1,
            addressee= self.user4
        )

        self.friendship4 = FriendshipModels.Friendship(
            status=FriendshipModels.FriendshipStatus.rejected,
            requester= self.user2,
            addressee= self.user4
        )

        self.friendship5 = FriendshipModels.Friendship(
            status=FriendshipModels.FriendshipStatus.pending,
            requester= self.user3,
            addressee= self.user4
        )

        users = [self.user1, self.user2, self.user3, self.user4]
        friendships = [self.friendship1, self.friendship2, self.friendship3, self.friendship4, self.friendship5]

        self.db.add_all(users)
        self.db.add_all(friendships)
        self.db.flush()

        for user in users:
            self.db.refresh(user)

        for friendship in friendships:
            self.db.refresh(friendship)

    #Get friendship
    def test_get_friendship_success(self): #success
        
        friendship = friendships_services.get_friendship(
            friendship_id=self.friendship1.id,
            db=self.db
        )

        self.assertIs(friendship, self.friendship1)
        self.assertEqual(friendship.addressee, self.user2)
        self.assertEqual(friendship.requester, self.user1)

    
    def test_get_friendship_not_found(self): #not found

        with self.assertRaises(exceptions.FriendShipNotFound):
            friendship=friendships_services.get_friendship(
            friendship_id=None,
            db=self.db
        )
            
    
    #Create friend requests
    def test_create_friend_requests_success(self): #success
        created_request = friendships_services.create_friend_request(
            self.user2,
            addressee_id=self.user3.id,
            db=self.db
        )

        self.assertEqual(created_request.status, FriendshipModels.FriendshipStatus.pending)
        self.assertEqual(created_request.addressee, self.user3)
        self.assertEqual(created_request.requester, self.user2)

    
    def test_create_friend_requests_already_exists(self): #already exists
        with self.assertRaises(exceptions.FriendRequestAlreadyExists):
            friendships_services.create_friend_request(
            self.user1,
            addressee_id=self.user2.id,
            db=self.db
        )
        
        with self.assertRaises(exceptions.FriendRequestAlreadyExists):
            friendships_services.create_friend_request(
            self.user1,
            addressee_id=self.user4.id,
            db=self.db
        )
    
    #Accept friend request
    def test_accept_friend_request_success(self): #success
        accepted_friendship = friendships_services.accept_friend_request(
            friendship_id=self.friendship3.id,
            current_user=self.user4,
            db=self.db
        )

        self.assertEqual(accepted_friendship.status, FriendshipModels.FriendshipStatus.accepted)
        self.assertIs(accepted_friendship, self.friendship3)
    
    def test_accept_friend_request_permission_denied(self): #permission denied exception
        with self.assertRaises(exceptions.PermissionDeniedException):
            friendships_services.accept_friend_request(
                friendship_id=self.friendship1.id,
                current_user=self.user4,
                db=self.db
            )

    def test_accept_friend_request_already_accepted(self): #already accepted
        with self.assertRaises(exceptions.FriendRequestAlreadyAccepted):
            friendships_services.accept_friend_request(
                friendship_id=self.friendship1.id,
                current_user=self.user2,
                db=self.db
            )
    
    def test_accept_friend_request_already_rejected(self): #already rejected
        with self.assertRaises(exceptions.FriendRequestAlreadyRejected):
            friendships_services.accept_friend_request(
                friendship_id=self.friendship4.id,
                current_user=self.user4,
                db=self.db
            )
    
    #Reject friend request
    def test_reject_friend_request_success(self): #success
        rejected_friendship = friendships_services.reject_friend_request(
            friendship_id=self.friendship3.id,
            current_user=self.user4,
            db=self.db
        )

        self.assertEqual(rejected_friendship.status, FriendshipModels.FriendshipStatus.rejected)
        self.assertIs(rejected_friendship, self.friendship3)

    
    def test_reject_friend_request_permission_denied(self): #permission denied exception
        with self.assertRaises(exceptions.PermissionDeniedException):
            friendships_services.reject_friend_request(
                friendship_id=self.friendship3.id,
                current_user=self.user3,
                db=self.db
            )

        
    def test_reject_friend_request_already_rejected(self): #already rejected
        with self.assertRaises(exceptions.FriendRequestAlreadyRejected):
            friendships_services.reject_friend_request(
                friendship_id=self.friendship4.id,
                current_user=self.user4,
                db=self.db
            )

    
    def test_reject_friend_request_already_accepted(self): #already accepted
        with self.assertRaises(exceptions.FriendRequestAlreadyAccepted):
            friendships_services.reject_friend_request(
                friendship_id=self.friendship1.id,
                current_user=self.user2,
                db=self.db
            )
    
    #Remove friendship
    def test_remove_friendship_sucess(self): #success
        removed_friendship = friendships_services.remove_friendship(
            friendship_id=self.friendship1.id,
            current_user=self.user1,
            db=self.db
        )

        self.assertIsNone(removed_friendship)


    def test_remove_friendship_permission_denied(self): #permission denied exception
        with self.assertRaises(exceptions.PermissionDeniedException):
            friendships_services.remove_friendship(
                friendship_id=self.friendship1.id,
                current_user=self.user3,
                db=self.db
            )
    
    #Get friend requests
    def test_get_friend_requests_empty(self): #success and empty friend requests
        friend_requests_list = friendships_services.get_friend_requests(
            current_user=self.user1,
            db=self.db
        )

        self.assertEqual(friend_requests_list, [])

    
    def test_get_friend_request_success(self): #success
        friend_requests_list = friendships_services.get_friend_requests(
            current_user=self.user4,
            db=self.db
        )

        self.assertEqual(len(friend_requests_list), 2)
        self.assertIn(self.friendship5, friend_requests_list)
        self.assertIn(self.friendship3, friend_requests_list)

    #Get friends
    def test_get_friends_empty(self): #success and empty friends list
        friends_list = friendships_services.get_friends(
            current_user=self.user4,
            db=self.db
        )

        self.assertEqual(friends_list, [])

    
    def test_get_friends_success(self): #success
        friends_list = friendships_services.get_friends(
            current_user=self.user1,
            db=self.db
        )

        self.assertEqual(len(friends_list), 2)
        self.assertIn(self.user2, friends_list)
        self.assertIn(self.user3, friends_list)
        
        


if __name__ == "__main__":
    unittest.main()