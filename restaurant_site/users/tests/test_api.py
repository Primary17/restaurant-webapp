from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserAuthAPITests(APITestCase):
    def test_register_returns_jwt_and_user(self):
        response = self.client.post(
            '/api/users/register/',
            {
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'StrongPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')
        self.assertEqual(response.data['user']['role'], User.ROLE_CUSTOMER)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_returns_tokens_and_user_payload(self):
        User.objects.create_user(username='loginuser', password='Secret123!')
        response = self.client.post(
            '/api/users/login/',
            {'username': 'loginuser', 'password': 'Secret123!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['username'], 'loginuser')

    def test_me_requires_authentication(self):
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_profile_for_authenticated_user(self):
        user = User.objects.create_user(
            username='meuser',
            password='pass',
            email='me@example.com',
        )
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'meuser')
        self.assertEqual(response.data['email'], 'me@example.com')
