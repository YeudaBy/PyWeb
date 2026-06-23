import threading
import time
from typing import Callable, Optional, Any


class MessageEvent:
    def __init__(self, data: Any):
        self.data = data


class WebSocket:
    def __init__(self, url: str):
        self.url = url
        self.onopen: Optional[Callable[[], None]] = None
        self.onmessage: Optional[Callable[[MessageEvent], None]] = None
        self.onclose: Optional[Callable[[], None]] = None
        self.onerror: Optional[Callable[[Exception], None]] = None

        # Automatically trigger mock onopen asynchronously to simulate handshake
        def open_connection() -> None:
            time.sleep(0.05)
            if self.onopen:
                try:
                    self.onopen()
                except Exception as e:
                    if self.onerror:
                        self.onerror(e)

        threading.Thread(target=open_connection, daemon=True).start()

    def send(self, data: str) -> None:
        # If wss://echo.websocket.org is used, simulate echo back
        if "echo" in self.url and self.onmessage:
            def echo_back() -> None:
                time.sleep(0.05)
                if self.onmessage:
                    try:
                        self.onmessage(MessageEvent(data))
                    except:
                        pass
            threading.Thread(target=echo_back, daemon=True).start()

    def close(self) -> None:
        if self.onclose:
            try:
                self.onclose()
            except:
                pass
        # Clear callbacks
        self.onopen = None
        self.onmessage = None
        self.onclose = None
        self.onerror = None
