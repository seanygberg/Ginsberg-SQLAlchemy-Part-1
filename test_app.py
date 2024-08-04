import unittest
from app import app, db
from models import User

class BloglyTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_blogly'
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            user = User(first_name="Test", last_name="User", image_url="http://example.com/image.jpg")
            db.session.add(user)
            db.session.commit()
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    def test_list_users(self):
        with self.client as client:
            resp = client.get('/users')
            self.assertIn(b'Test User', resp.data)

    def test_show_user(self):
        with self.client as client:
            user = User.query.first()
            resp = client.get(f'/users/{user.id}')
            self.assertIn(b'Test User', resp.data)

    def test_add_user(self):
        with self.client as client:
            data = {
                'first_name': 'New',
                'last_name': 'User',
                'image_url': 'http://example.com/new_image.jpg'
            }
            resp = client.post('/users/new', data=data, follow_redirects=True)
            self.assertIn(b'New User', resp.data)

    def test_edit_user(self):
        with self.client as client:
            user = User.query.first()
            data = {
                'first_name': 'Updated',
                'last_name': 'User',
                'image_url': user.image_url
            }
            resp = client.post(f'/users/{user.id}/edit', data=data, follow_redirects=True)
            self.assertIn(b'Updated User', resp.data)

    def test_add_post(self):
        with self.client as client:
            user = User.query.first()
            data = {
                'title': 'New Post',
                'content': 'This is the content of the new post.'
            }
            resp = client.post(f'/users/{user.id}/posts/new', data=data, follow_redirects=True)
            self.assertIn(b'New Post', resp.data)
    
    def test_show_post(self):
        with self.client as client:
            user = User.query.first()
            post = Post(title='Test Post', content='Test Content', user_id=user.id)
            db.session.add(post)
            db.session.commit()
            
            resp = client.get(f'/posts/{post.id}')
            self.assertIn(b'Test Post', resp.data)

    def test_edit_post(self):
        with self.client as client:
            user = User.query.first()
            post = Post(title='Test Post', content='Test Content', user_id=user.id)
            db.session.add(post)
            db.session.commit()
            
            data = {
                'title': 'Updated Post',
                'content': 'Updated content.'
            }
            resp = client.post(f'/posts/{post.id}/edit', data=data)
            self.assertIn(b'Updated Post', resp.data)

    def test_delete_post(self):
        with self.client as client:
            user = User.query.first()
            post = Post(title='Test Post', content='Test Content')
            db.session.add(post)
            db.session.commit()
            
            resp = client.post(f'/posts/{post.id}/delete')
            self.assertNotIn(b'Test Post', resp.data)