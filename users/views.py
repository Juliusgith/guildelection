from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import User, AuthorizedVoter
from .forms import RegistrationForm, LoginForm, ProfileUpdateForm
import logging
logger = logging.getLogger(__name__)
from django.conf import settings  # Add this import
from voting.models import Vote  # Import the Vote model

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data.get('full_name')
            registration_number = form.cleaned_data.get('registration_number')

            try:
                # Check if the user is an authorized voter
                authorized_voter = AuthorizedVoter.objects.get(
                    registration_number=registration_number
                )

                # Validate that the name matches
                if authorized_voter.full_name.lower() != full_name.lower():
                    messages.error(request, "Your name does not match our records for this Program/course.")
                    return render(request, 'users/register.html', {'form': form})

                # Ensure that the voter hasn't registered already
                if authorized_voter.has_registered:
                    messages.error(request, "This registration number has already been registered.")
                    return render(request, 'users/register.html', {'form': form})

                # Save the user if validation passes
                user = form.save(commit=False)
                user.is_active = True
                user.is_verified = False
                user.faculty = authorized_voter.faculty
                user.year_of_study = authorized_voter.year_of_study
                user.save()

                # Mark the authorized voter as registered
                authorized_voter.has_registered = True
                authorized_voter.save()

                # Send verification email
                verification_token = user.verification_token
                verification_url = request.build_absolute_uri(f"/users/verify/{verification_token}/")

                subject = "Verify Your Account"
                html_message = render_to_string('users/email_verification.html', {
                    'user': user,
                    'verification_url': verification_url
                })
                plain_message = strip_tags(html_message)

                logger.info(f"Attempting to send verification email to {user.email}")
                try:
                    send_mail(
                        subject,
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,  # Use settings.DEFAULT_FROM_EMAIL
                        [user.email],
                        html_message=html_message
                    )
                    logger.info(f"Verification email sent to {user.email}")
                except Exception as e:
                    logger.error(f"Failed to send verification email: {e}")
                    messages.error(request, f"There was an error sending the verification email: {e}")
                    return render(request, 'users/register.html', {'form': form})

                messages.success(request, "Registration successful! Please check your email to verify your account.")
                return redirect('users:verification_sent')

            except AuthorizedVoter.DoesNotExist:
                # Handle the case where no authorized voter was found
                logger.error(f"Registration failed: No authorized voter found for program/course {registration_number}")
                messages.error(request, "Registration failed. Your Program/Course is not the same as in our authorized voters list.", extra_tags='error-red')
                return render(request, 'users/register.html', {'form': form})

    else:
        form = RegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def verification_sent(request):
    """
    View to inform the user that they need to check their email for verification.
    """
    return render(request, 'users/verification_sent.html')


def login_view(request):
    """
    Handles user login, including authentication and email verification checks.
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')  # Use 'username' instead of 'registration_number'
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)  # Authenticate by username
            
            if user is not None:
                if not user.is_verified:
                    messages.error(request, "Please verify your email before logging in.")
                    return render(request, 'users/login.html', {'form': form})
                
                login(request, user)
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid credentials")
                return render(request, 'users/login.html', {'form': form})
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})

def verify_account(request, token):
    """
    Verifies a user's account using the provided token.
    """
    user = get_object_or_404(User, verification_token=token)
    
    # Check if token is still valid (24-hour expiry)
    if user.date_joined < timezone.now() - timedelta(days=1):
        return HttpResponseForbidden("Verification link has expired. Please contact administrator.")
    
    if not user.is_verified:
        user.is_verified = True
        user.save()
        messages.success(request, "Your account has been verified. You can now login.")
    else:
        messages.info(request, "Your account has already been verified.")
    
    return redirect('users:login')


@login_required
def profile_view(request):
    """
    Allows users to update their profile information and view their voting history.
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('users:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    # Fetch user's voting history
    user_votes = Vote.objects.filter(voter=request.user).select_related('election', 'candidate')

    return render(request, 'users/profile.html', {'form': form, 'user_votes': user_votes})


@login_required
def logout_view(request):
    """
    Logs out the current user and redirects them to the home page.
    """
    logout(request)
    return redirect('home')