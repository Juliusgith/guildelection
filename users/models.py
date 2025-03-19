from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

class AuthorizedVoter(models.Model):
    """Pre-loaded list of authorized voters"""
    full_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    faculty = models.CharField(max_length=100)
    year_of_study = models.IntegerField(default=1)
    has_registered = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.full_name} ({self.registration_number})"

class User(AbstractUser):
    """Custom user model with extended fields for university voting system"""
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)  # Keep this for reference
    faculty = models.CharField(max_length=100)
    year_of_study = models.IntegerField(null=True)
    program = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True)
    
    USERNAME_FIELD = 'username'  # Use 'username' as the unique identifier
    REQUIRED_FIELDS = ['email', 'full_name']  # Remove 'username' from REQUIRED_FIELDS

    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = get_random_string(64)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.registration_number})"