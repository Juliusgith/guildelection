# signals.py (create this file)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User

@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    """Send verification email when a new user is created"""
    if created and not instance.is_verified:
        subject = 'Verify your account for University Guild Council Voting'
        message = f"""
        Hello {instance.full_name},
        
        Thank you for registering for the University Guild Council Voting System.
        Please verify your account by clicking the link below:
        
        {settings.SITE_URL}/users/verify/{instance.verification_token}/
        
        This link will expire in 24 hours.
        
        If you did not register for this service, please ignore this email.
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]
        send_mail(subject, message, from_email, recipient_list)