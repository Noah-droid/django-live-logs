import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import datetime
import threading

def _send_to_channel(channel_layer, data):
    try:
        async_to_sync(channel_layer.group_send)("admin_live_logs", data)
    except Exception as e:
        print("LIVE LOGS BACKGROUND ERROR:", e)

class WebSocketLogHandler(logging.Handler):
    """
    Custom logging handler that intercepts logs and broadcasts them 
    to a Redis channel layer for real-time WebSocket streaming.
    """
    def emit(self, record):
        try:
            log_entry = self.format(record)
            channel_layer = get_channel_layer()
            
            if not channel_layer:
                return
                
            data = {
                "type": "log_message",
                "level": record.levelname,
                "message": log_entry,
                "module": record.module,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Run in a separate thread so it never blocks the main app
            # and avoids ASGI async_to_sync event loop conflicts.
            threading.Thread(target=_send_to_channel, args=(channel_layer, data), daemon=True).start()
            
        except Exception as e:
            # We must never crash the application just because a log failed to send
            print("LIVE LOGS ERROR:", e)
