"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows
from forms import EditProfileForm

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_show_user(self):
        """Test show user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testuser.username, html)

    def test_add_follow(self):
        """Test follow another user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(
                username='test2',
                password='password',
                email = 'test2@example.com'
            )
            db.session.add(self.testuser)
            db.session.add(user2)
            db.session.commit()

            self.assertFalse(self.testuser.is_following(user2))
            c.post(f"/users/follow/{user2.id}")
            self.assertTrue(self.testuser.is_following(user2))

    def test_stop_following(self):
        """Test stop following another user."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(
                username='test2',
                password='password',
                email = 'test2@example.com'
            )
            db.session.add(self.testuser)
            db.session.add(user2)
            db.session.commit()

            follow = Follows(
                user_being_followed_id = user2.id,
                user_following_id = self.testuser.id
            )
            db.session.add(follow)
            db.session.commit()

            self.assertTrue(self.testuser.is_following(user2))
            c.post(f"/users/stop-following/{user2.id}")
            self.assertFalse(self.testuser.is_following(user2))

    def test_edit_profile(self):
        """ Edit user profile """
        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id

            form = {
                'username': 'testuser',
                'email': "test@test.com",
                'password': "testuser",
                'image_url': '',
                'bio': 'Test User'
            }
            
            resp = c.post(f'/users/profile', data=form)
            user = User.query.filter_by(username='testuser').one()
            self.assertEqual(user.bio, 'Test User')

    def test_edit_profile_error(self):
        """ Edit user profile failure"""
        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id

            form = {
                'username': '',
                'email': "",
                'password': "",
                'image_url': '',
                'bio': 'Test User'
            }
            
            resp = c.post(f'/users/profile', data=form)
            user = User.query.filter_by(username='testuser').one()
            self.assertIsNone(user.bio)

    def test_delete_user(self):
        """Test delete user"""
        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id

            
            user2 = User(
                username = 'testuser2',
                password = 'password',
                email = 'testuser2@example.com'
            )
            db.session.add(user2)
            db.session.commit()

            message = Message(
                text = 'Test Message',
                user_id = self.testuser.id
            )
            message2 = Message(
                text = 'Test Message for 2',
                user_id = user2.id
            )
            db.session.add(message)
            db.session.add(message2)
            db.session.commit()
            
            c.post(f'/users/delete')
            users = User.query.all()
            self.assertEqual(len(users), 1)
            msgs = Message.query.all()
            self.assertEqual(len(msgs), 1)

    def test_add_like(self):
        """Test message like"""
        with self.client as c:
            with c.session_transaction() as s:
                s[CURR_USER_KEY] = self.testuser.id

            user2 = User(
            username = 'testuser2',
            password = 'password',
            email = 'testuser2@example.com'
            )
            db.session.add(self.testuser)
            db.session.add(user2)
            db.session.commit()

            message = Message(
                text = 'Test Message 1',
                user_id = user2.id
            )
            message2 = Message(
                text = 'Test Message 2',
                user_id = user2.id
            )
            db.session.add(message)
            db.session.add(message2)
            db.session.commit()

            c.post(f'users/add_like/{message.id}')
            self.assertTrue(message.is_liked(self.testuser))
            self.assertFalse(message2.is_liked(self.testuser))