# Django Live Logs

**A lightweight, zero-configuration package that streams your Django server logs directly to a beautiful, real-time web dashboard using WebSockets and Redis.**

![Django Live Logs Dashboard](https://i.imgur.com/placeholder.png) *(Imagine a beautiful dark-mode dashboard here)*

## Features
- 🚀 **Real-Time Streaming**: Uses Django Channels and Redis to push logs instantly.
- 🎨 **Built-In Dashboard**: Comes with a sleek, dark-mode Tailwind CSS interface out of the box.
- 🛡️ **Secure by Default**: Dashboard and WebSockets are natively protected by Django's `@staff_member_required` and Session cookies.
- 🧵 **Non-Blocking**: Dispatches logs in a background thread to prevent ASGI async event loop collisions.
- 🔍 **Filtering**: Instantly filter between `INFO`, `WARNING`, and `ERROR` logs.

---

## 1. Installation

Install the package via pip:
```bash
pip install django-live-logs
```

*Note: This package requires `channels` and `channels-redis` to be installed and configured in your project.*

## 2. Configuration

### Step A: Update `settings.py`
Add the package to your installed apps:
```python
INSTALLED_APPS = [
    # ...
    'django_live_logs',
]
```

**Authentication Options:**
By default, the dashboard requires users to be logged into the standard Django Admin interface as a Superuser.
If you prefer to use a shared team password instead of Django sessions, simply add this variable:
```python
LIVE_LOGS_PASSWORD = "your-secure-team-password"
```

Configure your `LOGGING` dictionary to catch everything (the root logger) and send it to the WebSocket handler:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'websocket': {'class': 'django_live_logs.handlers.WebSocketLogHandler'},
    },
    'root': {
        'handlers': ['console', 'websocket'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'websocket'],
            'level': 'INFO',
            'propagate': False,
        }
    },
}
```

### Step B: Route the Dashboard (HTTP)
In your main `urls.py`, include the dashboard URL:
```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('live-logs/', include('django_live_logs.urls')),
]
```

### Step C: Route the WebSockets (ASGI)
In your `asgi.py`, you need to route the WebSockets. Because `django-live-logs` uses the Django Admin session to authenticate the UI, it requires Django's `AuthMiddlewareStack`.

If your entire application uses Session Auth, simply wrap your `URLRouter`:

```python
from channels.auth import AuthMiddlewareStack
from django.urls import path, include
import django_live_logs.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                your_app_routing.websocket_urlpatterns + 
                django_live_logs.routing.websocket_urlpatterns
            )
        )
    ),
})
```

**Advanced: Using JWT / Custom Auth in your main app?**
If your main application uses custom JWT auth and you want to completely isolate `AuthMiddlewareStack` so it doesn't interfere with your custom websockets, use a direct mapping in your `URLRouter`. This is the most reliable way to avoid routing conflicts:

```python
from django.urls import re_path
from channels.auth import AuthMiddlewareStack
import django_live_logs.consumers
import your_app_routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        URLRouter([
            # 1. Map Live Logs directly to its consumer with Session Auth
            re_path(r"^ws/live-logs/$", AuthMiddlewareStack(django_live_logs.consumers.LiveLogConsumer.as_asgi())),
            
            # 2. Map everything else to your custom Token Auth
            re_path(r"^", YourTokenAuthMiddleware(URLRouter(your_app_routing.websocket_urlpatterns))),
        ])
    ),
})
```

---

## 3. Usage
Simply run your Django server:
```bash
python manage.py runserver
```

Navigate to `/live-logs/` in your browser. 
If `LIVE_LOGS_PASSWORD` is configured, type in your team password.
If not, it will fall back to requiring a standard Django superuser session. Once authenticated, the dark mode dashboard will connect via WebSockets, and any `logging.info()`, `logging.error()`, etc., triggered anywhere in your backend will stream to your screen instantly!

---

## Troubleshooting & Production

### CSRF & Origin Headers (403 Forbidden)
If you deploy your app behind a reverse proxy (like Nginx) with HTTPS, Django's security middleware or Channels' `AllowedHostsOriginValidator` might block your connections. Ensure your `settings.py` is configured with your production domains:

```python
ALLOWED_HOSTS = ["your-domain.com"]

# Trust your domain for CSRF and WebSocket origins
CSRF_TRUSTED_ORIGINS = [
    "https://your-domain.com",
    "http://your-domain.com",
]
```

## How it Works
The custom `WebSocketLogHandler` intercepts Python logs. Instead of blocking the main thread, it tosses the log payload to a daemon thread. The daemon thread safely uses `async_to_sync` to dispatch the JSON payload to the Redis Channel Layer. Finally, the Django Channels WebSocket consumer securely beams it to the authenticated frontend UI.
