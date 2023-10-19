"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_is_following(self):

        user1 = User(
            email = 'test1@example.com',
            username ='test1',
            password = 'password'
        )
        user2 = User(
            email = 'test2@example.com',
            username ='test2',
            password = 'password'
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        follow = Follows(
            user_being_followed_id = user1.id,
            user_following_id = user2.id
        )

        db.session.add(follow)
        db.session.commit()

        self.assertEqual(user1.is_followed_by(user2), True)
        self.assertEqual(user2.is_followed_by(user1), False)
        self.assertEqual(user1.is_following(user2), False)
        self.assertEqual(user2.is_following(user1), True)

    def test_authentication(self):
        User.signup(
            'test_user',
            'test@example.com',
            'password',
            None
        )

        db.session.commit()

        self.assertIsInstance(User.authenticate('test_user', 'password'), User)
        self.assertFalse(User.authenticate('wrong_user', 'password'), False)
        self.assertFalse(User.authenticate('test_user', 'wrong_password'), False)
