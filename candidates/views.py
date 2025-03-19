from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db.models import Count
from django.db import models
from .models import Position, Candidate, CandidateApplication
from .forms import CandidateApplicationForm, PositionForm, ApplicationReviewForm
import logging

logger = logging.getLogger(__name__)

# Public views
def position_list(request):
    """Display all active positions with the count of approved candidates"""
    positions = Position.objects.filter(is_active=True).annotate(
        candidate_count=Count('candidates', filter=models.Q(candidates__is_approved=True))
    )
    return render(request, 'candidates/position_list.html', {'positions': positions})

def position_detail(request, id):
    """Display a position and its approved candidates with the count"""
    position = get_object_or_404(Position, id=id, is_active=True)
    candidates = position.candidates.filter(is_approved=True)  # Ensure only approved candidates are included
    candidate_count = candidates.count()  # Count the approved candidates
    return render(request, 'candidates/position_detail.html', {
        'position': position,
        'candidates': candidates,
        'candidate_count': candidate_count
    })

def candidate_detail(request, pk):
    """Display a candidate's profile"""
    candidate = get_object_or_404(Candidate, pk=pk, is_approved=True)
    position = candidate.position  # Ensure the candidate has a related position
    return render(request, 'candidates/candidate_detail.html', {
        'candidate': candidate,
        'position': position  # Pass the position to the template
    })
# Student views
@login_required
def apply_for_position(request):
    """Allow students to apply for a position"""
    pending_applications = CandidateApplication.objects.filter(user=request.user, status='pending')

    if request.method == 'POST':
        form = CandidateApplicationForm(request.POST, request.FILES, user=request.user)  # Pass user
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, "Your application has been submitted and is pending review.")
            logger.info(f"User {request.user.full_name} applied for position {application.position.title}.")
            return redirect('candidates:my_applications')
    else:
        form = CandidateApplicationForm(user=request.user)  # Ensure user is passed

    return render(request, 'candidates/apply_form.html', {
        'form': form,
        'pending_applications': pending_applications
    })



from .models import GlobalSettings

def apply_for_position(request):
    """Allow students to apply for a position"""
    # Get the global settings object (create it if it doesn't exist)
    global_settings = GlobalSettings.objects.first() or GlobalSettings.objects.create()
    is_application_active = global_settings.application_status == 'active'

    if not is_application_active:
        messages.warning(request, "Applications are currently closed. Please check back later.")
        return redirect('candidates:position_list')

    pending_applications = CandidateApplication.objects.filter(user=request.user, status='pending')

    if request.method == 'POST':
        form = CandidateApplicationForm(request.POST, request.FILES, user=request.user)  # Pass user
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, "Your application has been submitted and is pending review.")
            logger.info(f"User {request.user.full_name} applied for position {application.position.title}.")
            return redirect('candidates:my_applications')
    else:
        form = CandidateApplicationForm(user=request.user)  # Ensure user is passed

    return render(request, 'candidates/apply_form.html', {
        'form': form,
        'pending_applications': pending_applications,
        'is_application_active': is_application_active
    })

@login_required
def my_applications(request):
    """Display a student's applications"""
    applications = CandidateApplication.objects.filter(user=request.user)
    return render(request, 'candidates/my_applications.html', {'applications': applications})

@login_required
def withdraw_application(request, pk):
    """Allow students to withdraw pending applications"""
    application = get_object_or_404(CandidateApplication, pk=pk, user=request.user)
    
    if application.status != 'pending':
        messages.error(request, "You can only withdraw pending applications.")
        return redirect('candidates:my_applications')
    
    if request.method == 'POST':
        application.delete()
        messages.success(request, "Your application has been withdrawn.")
        logger.info(f"User {request.user.full_name} withdrew application for position {application.position.title}.")
        return redirect('candidates:my_applications')
    
    return render(request, 'candidates/withdraw_confirmation.html', {'application': application})

# Admin views
@staff_member_required
def admin_position_list(request):
    """Admin view to manage positions"""
    positions = Position.objects.all().annotate(
        candidate_count=Count('candidates', filter=models.Q(candidates__is_approved=True))
    )
    return render(request, 'candidates/admin/position_list.html', {'positions': positions})

@staff_member_required
def admin_position_create(request):
    """Admin view to create a new position"""
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save()
            messages.success(request, f"Position '{position.title}' has been created.")
            logger.info(f"Admin created position: {position.title}.")
            return redirect('candidates:admin_position_list')
    else:
        form = PositionForm()
    
    return render(request, 'candidates/admin/position_form.html', {'form': form, 'is_create': True})

@staff_member_required
def admin_position_edit(request, pk):
    """Admin view to edit an existing position"""
    position = get_object_or_404(Position, pk=pk)
    
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, f"Position '{position.title}' has been updated.")
            logger.info(f"Admin updated position: {position.title}.")
            return redirect('candidates:admin_position_list')
    else:
        form = PositionForm(instance=position)
    
    return render(request, 'candidates/admin/position_form.html', {
        'form': form, 
        'position': position,
        'is_create': False
    })

@staff_member_required
def admin_application_list(request):
    """Admin view to see all applications"""
    # Get filtering parameters
    status = request.GET.get('status', 'pending')
    position_id = request.GET.get('position')
    
    # Base queryset
    applications = CandidateApplication.objects.all()
    
    # Apply filters
    if status:
        applications = applications.filter(status=status)
    if position_id:
        applications = applications.filter(position_id=position_id)
    
    positions = Position.objects.all()
    
    return render(request, 'candidates/admin/application_list.html', {
        'applications': applications,
        'positions': positions,
        'current_status': status,
        'current_position': position_id
    })

@staff_member_required
def admin_application_review(request, pk):
    """Admin view to review a specific application"""
    application = get_object_or_404(CandidateApplication, pk=pk)
    
    if application.status != 'pending':
        messages.warning(request, f"This application has already been {application.get_status_display().lower()}.")
        return redirect('candidates:admin_application_list')
    
    if request.method == 'POST':
        form = ApplicationReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            
            if action == 'approve':
                candidate = application.approve()
                if candidate:
                    messages.success(request, f"Application approved. {application.user.full_name} is now a candidate for {application.position.title}.")
                    logger.info(f"Admin approved application for {application.user.full_name} - {application.position.title}.")
                else:
                    messages.error(request, "Failed to approve the application.")
                    logger.error(f"Failed to approve application for {application.user.full_name} - {application.position.title}.")
            else:
                reason = form.cleaned_data['rejection_reason']
                application.reject(reason)
                messages.success(request, f"Application rejected with reason provided.")
                logger.info(f"Admin rejected application for {application.user.full_name} - {application.position.title}.")
            
            return redirect('candidates:admin_application_list')
    else:
        form = ApplicationReviewForm()
    
    return render(request, 'candidates/admin/application_review.html', {
        'application': application,
        'form': form
    })

@staff_member_required
def admin_candidate_list(request):
    """Admin view to manage approved candidates"""
    position_id = request.GET.get('position')
    
    # Base queryset
    candidates = Candidate.objects.filter(is_approved=True)
    
    # Apply filter
    if position_id:
        candidates = candidates.filter(position_id=position_id)
    
    positions = Position.objects.all()
    
    return render(request, 'candidates/admin/candidate_list.html', {
        'candidates': candidates,
        'positions': positions,
        'current_position': position_id
    })

@staff_member_required
def admin_candidate_remove(request, pk):
    """Admin view to remove a candidate"""
    candidate = get_object_or_404(Candidate, pk=pk)
    
    if request.method == 'POST':
        # Get application if exists
        try:
            application = CandidateApplication.objects.get(user=candidate.user, position=candidate.position)
            application.status = 'rejected'
            application.rejection_reason = "Removed by administrator"
            application.save()
            logger.info(f"Admin removed candidate {candidate.user.full_name} from position {candidate.position.title}.")
        except CandidateApplication.DoesNotExist:
            logger.warning(f"No application found for candidate {candidate.user.full_name} - {candidate.position.title}.")
        
        candidate.delete()
        messages.success(request, f"{candidate.user.full_name} has been removed as a candidate for {candidate.position.title}.")
        return redirect('candidates:admin_candidate_list')
    
    return render(request, 'candidates/admin/candidate_remove.html', {'candidate': candidate})


