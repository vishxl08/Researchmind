import os
import django
from django.conf import settings

# Configure Django settings for tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

# Setup Django
django.setup()

# Common test fixtures and configuration
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def django_db_setup():
    """Override the Django database for testing"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def test_user():
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass123'
    }
