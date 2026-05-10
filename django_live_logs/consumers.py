from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings

class LiveLogConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Allow configuration of who can view logs. Defaults to superusers only.
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
