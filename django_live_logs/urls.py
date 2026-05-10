from django.urls import path
from . import views

urlpatterns = [
    path('live-logs/', views.live_logs_dashboard, name='live_logs_dashboard'),
]
