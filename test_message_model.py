"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Likes

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

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Likes.query.delete()

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""
        
        user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(user)
        db.session.commit()

        message = Message(
            text='test message',
            user_id = user.id
        )

        db.session.add(message)
        db.session.commit()

        # Message should have an author
        self.assertIsInstance(message.user, User)

    def test_is_liked(self):
        """ Does message show that a user liked it? """

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

        message = Message(
            text = 'Test Message',
            user_id = user1.id
        )

        db.session.add(message)
        db.session.commit()

        like = Likes(
            user_id = user2.id,
            message_id = message.id
        )

        db.session.add(like)
        db.session.commit()

        self.assertTrue(message.is_liked(user2))
        self.assertFalse(message.is_liked(user1))
