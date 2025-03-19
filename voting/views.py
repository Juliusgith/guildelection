from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.conf import settings  # Import settings for AUTH_USER_MODEL
from .models import Election, Candidate, Vote


def home(request):
    """
    Display active and past elections on the homepage.
    """
    active_elections = Election.objects.filter(is_active=True, end_date__gte=timezone.now())
    past_elections = Election.objects.filter(end_date__lt=timezone.now())
    
    return render(request, 'voting/home.html', {
        'active_elections': active_elections,
        'past_elections': past_elections
    })

from django.utils import timezone

def election_detail(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    candidates = election.candidates.all()
    now = timezone.now()

    # Check if the user has already voted
    user_voted = False
    user_choice = None
    if request.user.is_authenticated:
        try:
            vote = Vote.objects.get(voter=request.user, election=election)
            user_voted = True
            user_choice = vote.candidate
        except Vote.DoesNotExist:
            pass

    return render(request, 'voting/election_detail.html', {
        'election': election,
        'candidates': candidates,
        'user_voted': user_voted,
        'user_choice': user_choice,
        'now': now,  # Pass the current time to the template
    })

@login_required
def cast_vote(request, election_id):
    """
    Allows authenticated users to cast their vote in an election.
    """
    # Get the election object or return a 404 error if it doesn't exist
    election = get_object_or_404(Election, pk=election_id)

    # Check if the election is still active
    if election.end_date < timezone.now() or not election.is_active:
        messages.error(request, "This election is no longer active.")
        return redirect('voting:election_detail', election_id=election.id)

    # Check if the user has already voted in this election
    if Vote.objects.filter(voter=request.user, election=election).exists():
        messages.error(request, "You have already voted in this election.")
        return redirect('users:profile')  # Redirect user to profile after voting

    # Handle POST requests (form submission)
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        if not candidate_id:
            messages.error(request, "Please select a candidate.")
            return redirect('voting:election_detail', election_id=election.id)

        # Get the selected candidate or return a 404 error if it doesn't exist
        candidate = get_object_or_404(Candidate, pk=candidate_id, election=election)

        # Create the vote
        Vote.objects.create(
            voter=request.user,
            candidate=candidate,
            election=election
        )

        messages.success(request, "Your vote has been recorded successfully!")
        return redirect('users:profile')  # Redirect to profile to show voting history

    # If the request method is not POST, redirect back to the election detail page
    messages.error(request, "Invalid request method.")
    return redirect('voting:election_detail', election_id=election.id)

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Election, Candidate

def results(request, election_id):
    """
    Displays the results of a specific election.
    """
    election = get_object_or_404(Election, pk=election_id)
    candidates = election.candidates.all()

    # Calculate total votes
    total_votes = sum(candidate.votes.count() for candidate in candidates)

    # Prepare results with vote counts and percentages
    results = []
    for candidate in candidates:
        vote_count = candidate.votes.count()
        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
        results.append({
            'candidate': candidate,
            'votes': vote_count,
            'percentage': percentage,
        })

    # Sort results by votes (highest first)
    results.sort(key=lambda x: x['votes'], reverse=True)

    return render(request, 'voting/results.html', {
        'election': election,
        'total_votes': total_votes,
        'results': results,
        'now': timezone.now(),  # Pass current time for comparison
    })
# Admin views
@login_required
def admin_dashboard(request):
    """
    Display the admin dashboard with all elections.
    Only accessible by staff members.
    """
    # Restrict access to non-staff users
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    elections = Election.objects.all().order_by('-start_date')
    
    return render(request, 'voting/admin/dashboard.html', {
        'elections': elections
    })