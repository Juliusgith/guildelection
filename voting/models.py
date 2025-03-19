from django.db import models
from django.conf import settings  # Import settings to use AUTH_USER_MODEL

class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def vote_count(self):
        return self.votes.count()

class Vote(models.Model):
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure one vote per user per election
        unique_together = ('voter', 'election')
        
    def __str__(self):
        return f"{self.voter.username} voted for {self.candidate.name} in {self.election.title}"