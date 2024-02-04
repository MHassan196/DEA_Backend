from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models

class CustomUser(AbstractUser):
    name = models.CharField(max_length=100, default="Unknown")
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15, default="Unknown")
    password = models.CharField(max_length=128)
    address = models.TextField(default="Unknown")
    purpose = models.CharField(max_length=255, default="Unknown")
    otherPurpose = models.CharField(max_length=255, default="Unknown")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Add custom fields here, if needed

    def __str__(self):
        return self.username
    
