from django.db import models
from django.utils.text import slugify
from users.models import User

class Position(models.Model):
    """Model representing an election position/role"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    max_candidates = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']

class Candidate(models.Model):
    """Model representing an election candidate"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidate_profile')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    manifesto = models.TextField()
    photo = models.ImageField(upload_to='candidate_photos/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    votes_count = models.IntegerField(default=0)
    campaign_slogan = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'position']
        ordering = ['-votes_count', 'user__full_name']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.position.title}"
    
    @property
    def full_name(self):
        return self.user.full_name
    
    @property
    def faculty(self):
        return self.user.faculty
    
    @property
    def program(self):
        return self.user.program


class CandidateApplication(models.Model):
    """Model for students applying to be candidates"""
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='applications')
    manifesto = models.TextField()
    photo = models.ImageField(upload_to='candidate_applications/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    campaign_slogan = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'position']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.position.title} ({self.get_status_display()})"
    
    def approve(self):
        """Approve application and create candidate entry"""
        if self.status == 'pending':
            self.status = 'approved'
            self.save()
            
            # Create or update candidate
            candidate, created = Candidate.objects.update_or_create(
                user=self.user,
                position=self.position,
                defaults={
                    'manifesto': self.manifesto,
                    'photo': self.photo,
                    'campaign_slogan': self.campaign_slogan,
                    'is_approved': True
                }
            )
            return candidate
        return None
    
    def reject(self, reason=''):
        """Reject application with optional reason"""
        if self.status == 'pending':
            self.status = 'rejected'
            self.rejection_reason = reason
            self.save()
            return True
        return False
    
class GlobalSettings(models.Model):
    """Model to store global settings like application status"""
    APPLICATION_STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    
    application_status = models.CharField(
        max_length=20,
        choices=APPLICATION_STATUS_CHOICES,
        default='inactive',
        help_text="Enable or disable candidate applications globally."
    )
    
    class Meta:
        verbose_name_plural = "Global Settings"
    
    def __str__(self):
        return f"Applications are {self.application_status}"