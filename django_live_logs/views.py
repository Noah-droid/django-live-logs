from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def live_logs_dashboard(request):
    """
    Renders the live log dashboard UI.
    If LIVE_LOGS_PASSWORD is set, uses a simple team password.
    Otherwise, falls back to requiring a standard Django superuser session.
    """
    required_password = getattr(settings, 'LIVE_LOGS_PASSWORD', None)
    
    if required_password:
        if request.method == "POST":
            password = request.POST.get("password")
            if password == required_password:
                response = render(request, 'django_live_logs/dashboard.html')
                response.set_cookie('live_logs_auth', password, httponly=False)
                return response
            else:
                return render(request, 'django_live_logs/login.html', {"error": "Invalid password"})
                
        cookie_auth = request.COOKIES.get('live_logs_auth')
        if cookie_auth == required_password:
            return render(request, 'django_live_logs/dashboard.html')
            
        return render(request, 'django_live_logs/login.html')
    else:
        from django.contrib.admin.views.decorators import staff_member_required
        
        @staff_member_required
        def legacy_dashboard(req):
            return render(req, 'django_live_logs/dashboard.html')
            
        return legacy_dashboard(request)
