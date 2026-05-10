from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings

class LiveLogConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        required_password = getattr(settings, 'LIVE_LOGS_PASSWORD', None)
        
        if required_password:
            headers = self.scope.get('headers', [])
            auth_success = False
            for name, value in headers:
                if name == b'cookie':
                    cookie_str = value.decode('utf-8')
                    # Basic check for the exact auth token cookie
                    if f"live_logs_auth={required_password}" in cookie_str:
                        auth_success = True
                        break
            
            if not auth_success:
                await self.close(code=4003)
                return
        else:
            # Fallback to standard Django session check
            require_superuser = getattr(settings, 'LIVE_LOGS_REQUIRE_SUPERUSER', True)
            user = self.scope.get("user")
            if require_superuser and (not user or not user.is_superuser):
                await self.close(code=4003)
                return

        self.group_name = "admin_live_logs"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        # Send an initial welcome message so the client knows it's connected
        await self.send_json({
            "level": "INFO",
            "message": "Connected to django-live-logs stream.",
            "module": "system",
        })

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def log_message(self, event):
        """
        Receives the log from the Redis channel and sends it down the WebSocket
        """
        await self.send_json({
            "level": event.get("level"),
            "message": event.get("message"),
            "module": event.get("module"),
            "timestamp": event.get("timestamp")
        })
