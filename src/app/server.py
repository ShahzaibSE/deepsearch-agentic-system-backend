from fastapi import FastAPI
import uvicorn
from typing import Optional

class Server:
    _instance: Optional['Server'] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Server, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, app: FastAPI) -> None:
        if not self._initialized:
            self.app = app
            self._server: Optional[uvicorn.Server] = None
            self._config: Optional[uvicorn.Config] = None
            self._initialized = True

    def run(self) -> None:
        """Run the server synchronously (blocking)"""
        try:
            uvicorn.run(self.app, host="0.0.0.0", port=8000)
        except KeyboardInterrupt:
            print("Server stopped by user")
        finally:
            # Ensure cleanup happens
            self._cleanup()

    def config(self, host: str, port: int, **kwargs) -> 'Server':
        """Configure a server without starting it"""
        self._config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            **kwargs
        )
        return self

    def start(self) -> None:
        """Start the server with the configured settings"""
        if not self._config:
            raise RuntimeError("Server not configured. Call config() first.")
        
        try:
            self._server = uvicorn.Server(self._config)
            self._server.run()
        except KeyboardInterrupt:
            print("Server stopped by user")
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        """Clean up server resources"""
        if self._server:
            try:
                self._server.should_exit = True
            except Exception:
                pass
            self._server = None
        self._config = None

