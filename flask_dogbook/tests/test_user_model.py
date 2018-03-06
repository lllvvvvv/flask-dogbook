import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission

class UserModelCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password = 'cat')
        with self.assertRaises(AttributeError):
            u.password

    #def test_password_verification(self):
   #     u = User(password = '11111111')
   #     self.assertTrue(u.verify_password('11111111'))
   #     self.assertFalse(u.verity_password('22222222'))

    def test_password_salts_are_random(self):
        u = User(password = '11111111')
        u2 = User(password = '11111111')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_roles_and_permissions(self):
        u = User(email='john@example.com',password ='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))


    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='jo@example.com', password='at')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
