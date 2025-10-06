"""
WebSocket manager for real-time communication.
Handles WebSocket connections and broadcasts updates to connected clients.
"""

import json
import asyncio
from typing import Set, Dict, Any
from aiohttp import web, WSMsgType

from wifijam.core.logger import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasting."""
    
    def __init__(self):
        """Initialize WebSocket manager."""
        self.connections: Set[web.WebSocketResponse] = set()
    
    async def handle_connection(self, request: web.Request) -> web.WebSocketResponse:
        """
        Handle new WebSocket connection.
        
        Args:
            request: Web request object
        
        Returns:
            WebSocket response
        """
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.connections.add(ws)
        logger.info(f"WebSocket client connected. Total connections: {len(self.connections)}")
        
        try:
            # Send welcome message
            await ws.send_json({
                "type": "connected",
                "message": "Connected to WIFIjam server"
            })
            
            # Handle incoming messages
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_message(ws, data)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON received: {msg.data}")
                        await ws.send_json({
                            "type": "error",
                            "message": "Invalid JSON format"
                        })
                
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
        
        finally:
            self.connections.discard(ws)
            logger.info(f"WebSocket client disconnected. Total connections: {len(self.connections)}")
        
        return ws
    
    async def _handle_message(self, ws: web.WebSocketResponse, data: Dict[str, Any]) -> None:
        """
        Handle incoming WebSocket message.
        
        Args:
            ws: WebSocket connection
            data: Message data
        """
        msg_type = data.get('type')
        
        if msg_type == 'ping':
            await ws.send_json({
                "type": "pong",
                "timestamp": data.get('timestamp')
            })
        
        elif msg_type == 'subscribe':
            # Handle subscription to specific events
            logger.debug(f"Client subscribed to: {data.get('events')}")
        
        else:
            logger.warning(f"Unknown message type: {msg_type}")
    
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Message to broadcast
        """
        if not self.connections:
            return
        
        # Create tasks for sending to all connections
        tasks = []
        for ws in self.connections.copy():
            if not ws.closed:
                tasks.append(self._send_safe(ws, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_safe(self, ws: web.WebSocketResponse, message: Dict[str, Any]) -> None:
        """
        Safely send message to WebSocket connection.
        
        Args:
            ws: WebSocket connection
            message: Message to send
        """
        try:
            await ws.send_json(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self.connections.discard(ws)
    
    async def send_to(self, ws: web.WebSocketResponse, message: Dict[str, Any]) -> None:
        """
        Send message to specific WebSocket connection.
        
        Args:
            ws: WebSocket connection
            message: Message to send
        """
        if ws in self.connections and not ws.closed:
            await self._send_safe(ws, message)
    
    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len(self.connections)
    
    async def close_all(self) -> None:
        """Close all WebSocket connections."""
        logger.info("Closing all WebSocket connections")
        
        tasks = []
        for ws in self.connections.copy():
            if not ws.closed:
                tasks.append(ws.close())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.connections.clear()

