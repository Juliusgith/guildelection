from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import User, AuthorizedVoter

class UserAdminConfig(UserAdmin):
    search_fields = ('email', 'username', 'full_name', 'registration_number')
    list_filter = ('is_active', 'is_staff', 'faculty', 'is_verified')
    ordering = ('-date_joined',)
    list_display = ('username', 'registration_number', 'email', 'full_name', 'faculty', 'is_active', 'is_verified')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'full_name', 'registration_number', 'faculty', 'year_of_study')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'registration_number', 'faculty', 'year_of_study', 'password1', 'password2', 'is_active', 'is_staff', 'is_verified'),
        }),
    )

class AuthorizedVoterResource(resources.ModelResource):
    class Meta:
        model = AuthorizedVoter
        import_id_fields = ['registration_number']
        fields = ('full_name', 'registration_number', 'faculty', 'year_of_study')
        export_order = ('full_name', 'registration_number', 'faculty', 'year_of_study', 'has_registered')

class AuthorizedVoterAdmin(ImportExportModelAdmin):
    resource_class = AuthorizedVoterResource
    list_display = ['full_name', 'registration_number', 'faculty', 'year_of_study', 'has_registered']
    search_fields = ['full_name', 'registration_number']
    list_filter = ['faculty', 'year_of_study', 'has_registered']
    readonly_fields = ['has_registered']

admin.site.register(User, UserAdminConfig)
admin.site.register(AuthorizedVoter, AuthorizedVoterAdmin)