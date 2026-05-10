import unittest
from datetime import date
from fastapi import Response
from sqlalchemy import select
from backend.modules.auth import services as auth_services, schemas as auth_schemas
from backend.modules.users import models as usermodels
from backend.core import security, exceptions
from tests.test_base import BaseTestCase


class TestAuthServices(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.response = Response()

    
    #Register
    def test_register_user_success(self):
        user_data = auth_schemas.RegisterRequest(
            email="test1@example.com",
            first_name="Test",
            last_name="User",
            birth_date=date(year=2000, month=4, day=4),
            password="password123123",
            password_repeat="password123123"
        )

        user = auth_services.register_user(user_data=user_data, db=self.db)

        self.assertEqual(user.email, "test1@example.com")
        self.assertTrue(security.verify_password("password123123", user.password))
    

    def test_register_user_existing_email(self):
        existing_user = usermodels.User(
            email="test2@example.com",
            first_name="Test",
            last_name="User",
            password=security.hash_password("password123123"),
            birth_date=date(year=2000, month=4, day=4),
            is_active=True
        )

        self.db.add(existing_user)
        self.db.commit()

        user_data = auth_schemas.RegisterRequest(
            email="test2@example.com",
            first_name="Test2",
            last_name="User2",
            birth_date=date(year=2001, month=1, day=1),
            password="password123",
            password_repeat="password123"
        )

        #Existing email
        with self.assertRaises(exceptions.UserEmailAlreadyExists):
            auth_services.register_user(user_data=user_data, db=self.db)

    
    def test_register_user_password_mismatch(self):
        user_data = auth_schemas.RegisterRequest(
            email="newuser@example.com",
            first_name="New",
            last_name="User",
            birth_date=date(year=2000, month=1, day=1),
            password="password123",
            password_repeat="password123123"
        )

        #Password do not match
        with self.assertRaises(exceptions.ValidationError):
            auth_services.register_user(user_data=user_data, db=self.db)

    
    #Login
    def test_login_user_success(self):
        user = usermodels.User(
            email= "login@example.com",
            first_name="Login",
            last_name="User",
            birth_date=date(year=2000,month=2,day=2),
            password=security.hash_password("mypassword"),
            is_active=True
        )

        self.db.add(user)
        self.db.commit()

        token_data = auth_services.login_user(
            response=self.response,
            email="login@example.com",
            password="mypassword",
            db=self.db
        )

        self.assertIn("access_token", token_data)
        self.assertEqual(token_data["token_type"], "bearer")

    
    def test_login_user_invalid_credentials(self):
        user = usermodels.User(
            email="login2@example.com",
            first_name="Login2",
            last_name="User2",
            birth_date=date(year=1995, month=10, day=19),
            password=security.hash_password("password"),
            is_active=True
        )

        self.db.add(user)
        self.db.commit()

        #Invalid password
        with self.assertRaises(exceptions.InvalidCredentials):
            auth_services.login_user(
                response=self.response,
                email="login2@example.com",
                password="wrongpassword",
                db=self.db
            )
        
        #Non-existent email address
        with self.assertRaises(exceptions.InvalidCredentials):
            auth_services.login_user(
                response=self.response,
                email="worng@example.com",
                password="password",
                db=self.db
            )


    

if __name__ == "__main__":
    unittest.main()