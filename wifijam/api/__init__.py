"""
API module for WIFIjam.
Provides REST API and WebSocket server for frontend communication.
"""

from wifijam.api.server import APIServer
from wifijam.api.routes import setup_routes
from wifijam.api.websocket import WebSocketManager

__all__ = [
    "APIServer",
    "setup_routes",
    "WebSocketManager",
]

