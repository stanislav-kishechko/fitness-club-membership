from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.user.serializers import AuthTokenSerializer, UserSerializer


class UserSerializerTests(TestCase):
    def test_create_user_success(self):
        payload = {
            "email": "test@example.com",
            "password": "strongpass123",
            "first_name": "John",
            "last_name": "Doe",
        }

        serializer = UserSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user.email, payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_password_is_write_only(self):
        payload = {
            "email": "test@example.com",
            "password": "strongpass123",
        }

        serializer = UserSerializer(data=payload)
        serializer.is_valid()
        data = serializer.data

        self.assertNotIn("password", data)

    def test_short_password_raises_error(self):
        payload = {
            "email": "test@example.com",
            "password": "123",
        }

        serializer = UserSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_is_staff_is_read_only(self):
        payload = {
            "email": "test@example.com",
            "password": "strongpass123",
            "is_staff": True,
        }

        serializer = UserSerializer(data=payload)
        serializer.is_valid()
        user = serializer.save()

        self.assertFalse(user.is_staff)

    def test_update_user_and_password(self):
        user = get_user_model().objects.create_user(
            email="user@example.com",
            password="oldpass123",
            first_name="Old",
        )

        payload = {
            "first_name": "New",
            "password": "newpass123",
        }

        serializer = UserSerializer(
            instance=user,
            data=payload,
            partial=True,
        )
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()
        updated_user.refresh_from_db()

        self.assertEqual(updated_user.first_name, payload["first_name"])
        self.assertTrue(updated_user.check_password(payload["password"]))


class AuthTokenSerializerTests(TestCase):
    def test_valid_credentials(self):
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email="user@example.com",
            password=password,
        )

        serializer = AuthTokenSerializer(data={"email": user.email, "password": password})

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], user)

    def test_invalid_credentials(self):
        get_user_model().objects.create_user(
            email="user@example.com",
            password="correctpass123",
        )

        serializer = AuthTokenSerializer(
            data={"email": "user@example.com", "password": "wrongpass"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_user_inactive(self):
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email="user@example.com",
            password=password,
        )
        user.is_active = False
        user.save()

        serializer = AuthTokenSerializer(data={"email": user.email, "password": password})

        self.assertFalse(serializer.is_valid())

    def test_missing_fields(self):
        serializer = AuthTokenSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertIn("password", serializer.errors)
