import unittest

from tests.test_base import BaseTestCase
from backend.modules.users import services as user_services, models, schemas
from backend.core import exceptions, security
from datetime import date


class TestUserServices(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user1 = models.User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            birth_date=date(year=2000, month=1, day=1),
            password=security.hash_password("password123"),
            is_active=True
        )

        self.user2 = models.User(
            email="test2@example.com",
            first_name="Test2",
            last_name="User2",
            birth_date=date(year=1995, month=1, day=1),
            password=security.hash_password("password"),
            is_active=True
        )
        

        self.db.add(self.user1)
        self.db.add(self.user2)
        self.db.flush()
        self.db.refresh(self.user1)
        self.db.refresh(self.user2)


    #update_user
    def test_update_profile_success(self):
        update_data= schemas.UserUpdate(
            first_name="Update",
            last_name="Name"
        )

        updated_user = user_services.update_profile(
            current_user=self.user1,
            user_update_data=update_data,
            db=self.db
        )

        self.assertEqual(updated_user.first_name, "Update")
        self.assertEqual(updated_user.last_name, "Name")


    def test_update_password_success(self):
        update_data = schemas.UserUpdate(
            password="newpassword",
            password_repeat="newpassword"
        )

        updated_user = user_services.update_profile(
            current_user=self.user1,
            user_update_data=update_data,
            db=self.db
        )

        self.assertTrue(security.verify_password("newpassword", updated_user.password))

    
    def test_update_password_mismatch(self):
        update_data = schemas.UserUpdate(
            password="newpassword123",
            password_repeat="newpassword"
        )

        with self.assertRaises(exceptions.ValidationError):
            user_services.update_profile(
            current_user=self.user1,
            user_update_data=update_data,
            db=self.db
        )
            
    def test_update_email_success(self):
        update_data = schemas.UserUpdate(
            email="NewEmail@example.com"
        )

        updated_user = user_services.update_profile(
            current_user=self.user1,
            user_update_data=update_data,
            db=self.db
        )

        self.assertEqual(updated_user.email, "NewEmail@example.com")

    
    def test_update_email_already_exists(self):
        update_data = schemas.UserUpdate(
            email="test2@example.com"
        )

        with self.assertRaises(exceptions.UserEmailAlreadyExists):
            user_services.update_profile(
                current_user=self.user1,
                user_update_data=update_data,
                db=self.db
            )

    #Delete user
    def test_delete_user_success(self):
        delete_data = schemas.UserDelete(
            is_active=False
        )

        deleted_user = user_services.delete_user(
            user_delete_data=delete_data,
            current_user=self.user1,
            db=self.db
        )
        
        self.db.refresh(self.user1)
        self.assertFalse(self.user1.is_active)

    
    def test_delete_user_not_found(self):
        delete_data = schemas.UserDelete()
        with self.assertRaises(exceptions.UserNotFound):
            user_services.delete_user(
                user_delete_data=delete_data,
                current_user=None,
                db=self.db
            )

    
    #get my profile
    def test_get_my_profile(self):
        my_profile = user_services.get_my_profile(
            current_user=self.user1,
            db=self.db
        )

        self.assertEqual(my_profile.email, self.user1.email)
        self.assertIs(my_profile, self.user1)


    #get all profiles
    def test_get_all_profiles(self):
        all_profiles = user_services.get_all_profiles(
            current_user=self.user1,
            db= self.db
        )

        self.assertEqual(len(all_profiles), 2)
        self.assertIn(self.user1, all_profiles)
        self.assertIn(self.user2, all_profiles)
    

    #get profiles by first name
    def test_get_profiles_by_first_name(self):
        get_by_first_1 = user_services.get_profiles_by_first_name(
            first_name="Test",
            current_user=self.user2,
            db=self.db
        )
        
        get_by_first_2 = user_services.get_profiles_by_first_name(
            first_name="Test2",
            current_user=self.user1,
            db=self.db
        )
        
        self.assertIn(self.user1, get_by_first_1)
        self.assertIn(self.user2, get_by_first_2)


    
    

if __name__ == "__main__":
    unittest.main()
    
    

