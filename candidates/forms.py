from django import forms
from .models import CandidateApplication, Position, Candidate

class CandidateApplicationForm(forms.ModelForm):
    """Form for students to apply to be candidates"""
    class Meta:
        model = CandidateApplication
        fields = ['position', 'manifesto', 'campaign_slogan', 'photo']
        widgets = {
            'manifesto': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'campaign_slogan': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show active positions
        self.fields['position'].queryset = Position.objects.filter(is_active=True)
        self.fields['position'].widget.attrs['class'] = 'form-select'
        self.fields['photo'].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        position = cleaned_data.get('position')
        
        # Check if user already applied for this position
        if self.user and position and CandidateApplication.objects.filter(
            user=self.user, position=position
        ).exists():
            raise forms.ValidationError(f"You have already applied for the position of {position.title}")
            
        # Check if position has reached max candidates
        if position and Candidate.objects.filter(position=position, is_approved=True).count() >= position.max_candidates:
            raise forms.ValidationError(f"The maximum number of candidates for {position.title} has been reached")
            
        return cleaned_data


class PositionForm(forms.ModelForm):
    """Form for admin to create/edit positions"""
    class Meta:
        model = Position
        fields = ['title', 'description', 'max_candidates', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'max_candidates': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ApplicationReviewForm(forms.Form):
    """Form for reviewing candidate applications"""
    ACTIONS = (
        ('approve', 'Approve Application'),
        ('reject', 'Reject Application'),
    )
    
    action = forms.ChoiceField(choices=ACTIONS, widget=forms.RadioSelect)
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        reason = cleaned_data.get('rejection_reason')
        
        if action == 'reject' and not reason:
            raise forms.ValidationError("Please provide a reason for rejection")
            
        return cleaned_data