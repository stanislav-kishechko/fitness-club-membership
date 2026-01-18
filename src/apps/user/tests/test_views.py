from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token_obtain_pair")
ME_URL = reverse("user:manage")


class CreateUserViewTests(APITestCase):
    def test_create_user_success(self):
        payload = {
            "email": "test@example.com",
            "password": "strongpass123",
            "first_name": "John",
            "last_name": "Doe",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_create_user_invalid_password(self):
        payload = {
            "email": "test@example.com",
            "password": "123",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class CreateTokenViewTests(APITestCase):
    def test_create_token_success(self):
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email="user@example.com",
            password=password,
        )

        res = self.client.post(
            TOKEN_URL,
            {"email": user.email, "password": password},
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)

    def test_create_token_invalid_credentials(self):
        get_user_model().objects.create_user(
            email="user@example.com",
            password="correctpass123",
        )

        res = self.client.post(
            TOKEN_URL,
            {"email": "user@example.com", "password": "wrongpass"},
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class ManageUserViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpass123",
        )

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_profile_success(self):
        self.client.force_authenticate(user=self.user)

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)

    def test_update_user_profile_and_password(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "first_name": "Updated",
            "password": "newpass123",
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertTrue(self.user.check_password(payload["password"]))
