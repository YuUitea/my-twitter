from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountApiTests(TestCase):

    def setUp(self):
        # invoked before each test function is executed
        self.client = APIClient()
        self.user = self.create_user(
            username='admin',
            email='admin@wejoy.com',
            password='correct password',
        )

    def create_user(self, username, email, password):
        # password is encrypted
        # username and email need to be normalized
        return User.objects.create_user(username, email, password)

    def test_login(self):
        """
        test login function
        """
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # when login failed; http status code returns 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)

        # test password incorrect
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # test login failed
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # test successful login
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['email'], 'admin@wejoy.com')
        self.assertNotEqual(response.data['user'], None)

        # test logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # test initial status as logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # test not allowed status
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # test successful log out
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # test status after logging out
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'testuser',
            'email': 'test@wejoy.com',
            'password': 'pwmustbe6ormore',
        }

        # test fail request
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # test invalid email
        response = self.client.post(SIGNUP_URL, {
            'username': 'testuser',
            'email': 'user',
            'password': 'pwmustbe6ormore'
        })
        self.assertEqual(response.status_code, 400)

        # test invalid password length
        response = self.client.post(SIGNUP_URL, {
            'username': 'testuser',
            'email': 'test@wejoy.com',
            'password': 'pw'
        })
        self.assertEqual(response.status_code, 400)

        # test invalid username length
        response = self.client.post(SIGNUP_URL, {
            'username': 'testtesttesttesttesttoolong',
            'email': 'test@wejoy.com',
            'password': 'pwmustbe6ormore'
        })
        self.assertEqual(response.status_code, 400)

        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'testuser')

        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)
