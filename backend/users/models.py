from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Additional custom fields can go here if needed
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username
