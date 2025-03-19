from django.contrib import admin
from django.utils.html import format_html
from .models import Position, Candidate, CandidateApplication
import logging

logger = logging.getLogger(__name__)

# Register Position with a custom ModelAdmin
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'max_candidates', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')

admin.site.register(Position, PositionAdmin)

# Register Candidate with custom admin
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'get_email', 'get_position_applied', 'votes_count', 'is_approved')
    list_filter = ('is_approved', 'position')
    search_fields = ('user__full_name', 'position__title')

    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.admin_order_field = 'user__full_name'
    get_full_name.short_description = 'Full Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.admin_order_field = 'user__email'
    get_email.short_description = 'Email'

    def get_position_applied(self, obj):
        return obj.position.title
    get_position_applied.admin_order_field = 'position'
    get_position_applied.short_description = 'Position Applied'

admin.site.register(Candidate, CandidateAdmin)

# Register CandidateApplication with custom admin
class CandidateApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'status_display', 'campaign_slogan', 'created_at')
    list_filter = ('status', 'position')
    search_fields = ('user__full_name', 'position__title')
    actions = ['approve_applications', 'reject_applications']

    def status_display(self, obj):
        if obj.status == 'approved':
            return format_html('<span style="color: green;">Approved</span>')
        elif obj.status == 'rejected':
            return format_html('<span style="color: red;">Rejected</span>')
        else:
            return format_html('<span style="color: orange;">Pending</span>')
    status_display.short_description = 'Status'

    def approve_applications(self, request, queryset):
        """
        Admin action to approve selected applications.
        """
        approved_count = 0
        for application in queryset.filter(status='pending'):
            try:
                candidate = application.approve()
                if candidate:
                    logger.info(f"Admin approved application for {application.user.full_name} - {application.position.title}.")
                    approved_count += 1
                else:
                    logger.error(f"Failed to approve application for {application.user.full_name} - {application.position.title}.")
            except Exception as e:
                logger.error(f"Error approving application for {application.user.full_name}: {e}")
        self.message_user(request, f"Successfully approved {approved_count} application(s).")

    approve_applications.short_description = "Approve selected applications"

    def reject_applications(self, request, queryset):
        """
        Admin action to reject selected applications.
        """
        rejected_count = 0
        for application in queryset.filter(status='pending'):
            try:
                application.reject(reason="Rejected by admin.")
                logger.info(f"Admin rejected application for {application.user.full_name} - {application.position.title}.")
                rejected_count += 1
            except Exception as e:
                logger.error(f"Error rejecting application for {application.user.full_name}: {e}")
        self.message_user(request, f"Successfully rejected {rejected_count} application(s).")

    reject_applications.short_description = "Reject selected applications"

admin.site.register(CandidateApplication, CandidateApplicationAdmin)

from .models import GlobalSettings

@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('application_status',)
    fields = ('application_status',)
    help_texts = {
        'application_status': 'Enable or disable candidate applications globally.'
    }