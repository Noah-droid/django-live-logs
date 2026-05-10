from django.shortcuts import render
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def live_logs_dashboard(request):
    """
    Renders the live log dashboard UI.
    Requires the user to be logged into the standard Django admin.
    """
    return render(request, 'django_live_logs/dashboard.html')
