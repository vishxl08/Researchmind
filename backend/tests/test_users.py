import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test cases for User model"""

    def test_create_user(self):
        """Test creating a new user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.is_active is True
        assert user.is_staff is False

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(username='strtest')
        assert str(user) == 'strtest'

    def test_user_unique_username(self):
        """Test that usernames are unique"""
        User.objects.create_user(username='unique')
        with pytest.raises(Exception):  # IntegrityError
            User.objects.create_user(username='unique')


@pytest.mark.django_db
class TestUserAuthentication:
    """Test user authentication"""

    def test_check_password(self):
        """Test password checking"""
        user = User.objects.create_user(
            username='pwtest',
            password='mypassword'
        )
        assert user.check_password('mypassword') is True
        assert user.check_password('wrongpass') is False

    def test_set_password(self):
        """Test setting password"""
        user = User.objects.create_user(username='pwset')
        user.set_password('newpassword')
        user.save()
        assert user.check_password('newpassword') is True
