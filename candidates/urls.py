from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    # Public views
    path('positions/', views.position_list, name='position_list'),
    path('positions/<int:id>/', views.position_detail, name='position_detail'),
    path('candidates/<int:pk>/', views.candidate_detail, name='candidate_detail'),
    
    # Student views
    path('apply/', views.apply_for_position, name='apply'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('withdraw/<int:pk>/', views.withdraw_application, name='withdraw_application'),
    
    # Admin views
    path('admin/positions/', views.admin_position_list, name='admin_position_list'),
    path('admin/positions/create/', views.admin_position_create, name='admin_position_create'),
    path('admin/positions/edit/<int:pk>/', views.admin_position_edit, name='admin_position_edit'),
    path('admin/applications/', views.admin_application_list, name='admin_application_list'),
    path('admin/applications/review/<int:pk>/', views.admin_application_review, name='admin_application_review'),
    path('admin/candidates/', views.admin_candidate_list, name='admin_candidate_list'),
    path('admin/candidates/remove/<int:pk>/', views.admin_candidate_remove, name='admin_candidate_remove'),
]