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
If your main application uses custom JWT auth and you want to completely isolate `AuthMiddlewareStack` so it doesn't interfere with your custom websockets, use a branching router:

```python
from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from your_app.middleware import CustomTokenAuthMiddleware
import django_live_logs.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        URLRouter([
            # 1. Isolate Session Auth strictly to the Live Logs endpoint
            re_path(r"^ws/live-logs/", AuthMiddlewareStack(URLRouter(django_live_logs.routing.websocket_urlpatterns))),
            
            # 2. Use your custom JWT auth for everything else
            re_path(r"^", CustomTokenAuthMiddleware(URLRouter(your_app_routing.websocket_urlpatterns))),
        ])
    ),
})
```

---

## 3. Usage

1. Log into your standard Django Admin panel (e.g., `/admin/`).
2. Navigate to `/live-logs/` in your browser.
3. Click **Connect**.
4. Watch your server logs flow in real-time!

## How it Works
The custom `WebSocketLogHandler` intercepts Python logs. Instead of blocking the main thread, it tosses the log payload to a daemon thread. The daemon thread safely uses `async_to_sync` to dispatch the JSON payload to the Redis Channel Layer. Finally, the Django Channels WebSocket consumer securely beams it to the authenticated frontend UI.
