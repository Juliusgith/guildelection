from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    path('', views.home, name='home'),  # Homepage for the voting app
    path('election/<int:election_id>/', views.election_detail, name='election_detail'),
    path('election/<int:election_id>/vote/', views.cast_vote, name='cast_vote'),
    path('election/<int:election_id>/results/', views.results, name='results'),
    
    # Admin dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]