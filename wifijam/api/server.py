"""
Main API server for WIFIjam.
Provides REST API and WebSocket endpoints for the frontend.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional
from aiohttp import web
import aiohttp_cors

from wifijam.core.logger import get_logger
from wifijam.core.config import Config
from wifijam.core.system import get_system_detector
from wifijam.wifi.adapter import AdapterManager
from wifijam.wifi.scanner import NetworkScanner
from wifijam.wifi.monitor import MonitorMode
from wifijam.wifi.attack import AttackManager, AttackConfig, AttackType
from wifijam.api.websocket import WebSocketManager

logger = get_logger(__name__)


class APIServer:
    """Main API server class."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize API server.
        
        Args:
            config: Optional configuration object
        """
        self.config = config or Config()
        self.app = web.Application()
        self.ws_manager = WebSocketManager()
        
        # Core components
        self.system = get_system_detector()
        self.adapter_manager = AdapterManager()
        self.scanner: Optional[NetworkScanner] = None
        self.monitor_mode: Optional[MonitorMode] = None
        self.attack_manager: Optional[AttackManager] = None
        
        # Current state
        self.current_adapter: Optional[str] = None
        self.is_scanning = False
        self.is_attacking = False
        
        # Setup routes and middleware
        self._setup_routes()
        self._setup_cors()
        self._setup_static_files()
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        # System endpoints
        self.app.router.add_get('/api/system/info', self.get_system_info)
        self.app.router.add_get('/api/system/dependencies', self.get_dependencies)
        
        # Adapter endpoints
        self.app.router.add_get('/api/adapters', self.get_adapters)
        self.app.router.add_get('/api/adapters/{interface}', self.get_adapter)
        self.app.router.add_post('/api/adapters/{interface}/select', self.select_adapter)
        
        # Monitor mode endpoints
        self.app.router.add_post('/api/monitor/enable', self.enable_monitor_mode)
        self.app.router.add_post('/api/monitor/disable', self.disable_monitor_mode)
        self.app.router.add_get('/api/monitor/status', self.get_monitor_status)
        
        # Scanner endpoints
        self.app.router.add_post('/api/scan/start', self.start_scan)
        self.app.router.add_post('/api/scan/stop', self.stop_scan)
        self.app.router.add_get('/api/scan/networks', self.get_networks)
        self.app.router.add_get('/api/scan/status', self.get_scan_status)
        
        # Attack endpoints
        self.app.router.add_post('/api/attack/start', self.start_attack)
        self.app.router.add_post('/api/attack/stop', self.stop_attack)
        self.app.router.add_get('/api/attack/status', self.get_attack_status)
        
        # Configuration endpoints
        self.app.router.add_get('/api/config', self.get_config)
        self.app.router.add_post('/api/config', self.update_config)
        self.app.router.add_post('/api/config/reset', self.reset_config)
        
        # WebSocket endpoint
        self.app.router.add_get('/ws', self.websocket_handler)
    
    def _setup_cors(self) -> None:
        """Setup CORS for cross-origin requests."""
        if self.config.server.cors_enabled:
            cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })
            
            # Apply CORS to all routes
            for route in list(self.app.router.routes()):
                if not isinstance(route.resource, web.StaticResource):
                    cors.add(route)
    
    def _setup_static_files(self) -> None:
        """Setup static file serving for the dashboard."""
        # Serve dashboard files
        dashboard_dir = Path(__file__).parent.parent.parent / "dashboard.html"
        if dashboard_dir.parent.exists():
            self.app.router.add_static('/static', dashboard_dir.parent, name='static')
            self.app.router.add_get('/', self.serve_dashboard)
    
    async def serve_dashboard(self, request: web.Request) -> web.Response:
        """Serve the main dashboard HTML."""
        dashboard_file = Path(__file__).parent.parent.parent / "dashboard.html"
        if dashboard_file.exists():
            return web.FileResponse(dashboard_file)
        return web.Response(text="Dashboard not found", status=404)
    
    # System endpoints
    async def get_system_info(self, request: web.Request) -> web.Response:
        """Get system information."""
        try:
            info = self.system.get_info_dict()
            return web.json_response({
                "success": True,
                "data": info
            })
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def get_dependencies(self, request: web.Request) -> web.Response:
        """Get system dependencies status."""
        try:
            deps = self.system.check_dependencies()
            return web.json_response({
                "success": True,
                "data": deps
            })
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    # Adapter endpoints
    async def get_adapters(self, request: web.Request) -> web.Response:
        """Get list of WiFi adapters."""
        try:
            self.adapter_manager.refresh()
            adapters = self.adapter_manager.to_dict_list()
            return web.json_response({
                "success": True,
                "data": adapters
            })
        except Exception as e:
            logger.error(f"Error getting adapters: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def get_adapter(self, request: web.Request) -> web.Response:
        """Get specific adapter information."""
        try:
            interface = request.match_info['interface']
            adapter = self.adapter_manager.get_adapter(interface)
            
            if not adapter:
                return web.json_response({
                    "success": False,
                    "error": f"Adapter {interface} not found"
                }, status=404)
            
            return web.json_response({
                "success": True,
                "data": adapter.to_dict()
            })
        except Exception as e:
            logger.error(f"Error getting adapter: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def select_adapter(self, request: web.Request) -> web.Response:
        """Select an adapter for operations."""
        try:
            interface = request.match_info['interface']
            adapter = self.adapter_manager.get_adapter(interface)
            
            if not adapter:
                return web.json_response({
                    "success": False,
                    "error": f"Adapter {interface} not found"
                }, status=404)
            
            self.current_adapter = interface
            self.scanner = NetworkScanner(adapter)
            self.monitor_mode = MonitorMode(adapter)
            self.attack_manager = AttackManager(adapter)
            
            logger.info(f"Selected adapter: {interface}")
            
            return web.json_response({
                "success": True,
                "message": f"Adapter {interface} selected"
            })
        except Exception as e:
            logger.error(f"Error selecting adapter: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    # Monitor mode endpoints
    async def enable_monitor_mode(self, request: web.Request) -> web.Response:
        """Enable monitor mode on selected adapter."""
        try:
            if not self.monitor_mode:
                return web.json_response({
                    "success": False,
                    "error": "No adapter selected"
                }, status=400)
            
            self.monitor_mode.enable()
            
            await self.ws_manager.broadcast({
                "type": "monitor_mode",
                "data": {"enabled": True}
            })
            
            return web.json_response({
                "success": True,
                "message": "Monitor mode enabled"
            })
        except Exception as e:
            logger.error(f"Error enabling monitor mode: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def disable_monitor_mode(self, request: web.Request) -> web.Response:
        """Disable monitor mode on selected adapter."""
        try:
            if not self.monitor_mode:
                return web.json_response({
                    "success": False,
                    "error": "No adapter selected"
                }, status=400)
            
            self.monitor_mode.disable()
            
            await self.ws_manager.broadcast({
                "type": "monitor_mode",
                "data": {"enabled": False}
            })
            
            return web.json_response({
                "success": True,
                "message": "Monitor mode disabled"
            })
        except Exception as e:
            logger.error(f"Error disabling monitor mode: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def get_monitor_status(self, request: web.Request) -> web.Response:
        """Get monitor mode status."""
        try:
            if not self.monitor_mode:
                return web.json_response({
                    "success": True,
                    "data": {"enabled": False}
                })
            
            return web.json_response({
                "success": True,
                "data": {"enabled": self.monitor_mode.is_enabled()}
            })
        except Exception as e:
            logger.error(f"Error getting monitor status: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    # WebSocket handler
    async def websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections."""
        return await self.ws_manager.handle_connection(request)
    
    # Scanner endpoints implementation
    async def start_scan(self, request: web.Request) -> web.Response:
        """Start network scanning."""
        try:
            if not self.scanner:
                return web.json_response({
                    "success": False,
                    "error": "No adapter selected"
                }, status=400)

            data = await request.json()
            duration = data.get('duration', 30)
            channel = data.get('channel')

            # Network discovery callback
            def on_network_discovered(network):
                asyncio.create_task(self.ws_manager.broadcast({
                    "type": "network_discovered",
                    "data": network.to_dict()
                }))

            # Start scan in background
            asyncio.create_task(asyncio.to_thread(
                self.scanner.start_scan,
                duration=duration,
                channel=channel,
                callback=on_network_discovered
            ))

            self.is_scanning = True

            return web.json_response({
                "success": True,
                "message": "Scan started"
            })
        except Exception as e:
            logger.error(f"Error starting scan: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def stop_scan(self, request: web.Request) -> web.Response:
        """Stop network scanning."""
        try:
            if self.scanner:
                self.scanner.stop_scan()
                self.is_scanning = False

            return web.json_response({
                "success": True,
                "message": "Scan stopped"
            })
        except Exception as e:
            logger.error(f"Error stopping scan: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def get_networks(self, request: web.Request) -> web.Response:
        """Get discovered networks."""
        try:
            if not self.scanner:
                return web.json_response({
                    "success": True,
                    "data": []
                })

            networks = [net.to_dict() for net in self.scanner.get_networks()]
            return web.json_response({
                "success": True,
                "data": networks
            })
        except Exception as e:
            logger.error(f"Error getting networks: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def get_scan_status(self, request: web.Request) -> web.Response:
        """Get scan status."""
        try:
            return web.json_response({
                "success": True,
                "data": {
                    "is_scanning": self.is_scanning,
                    "network_count": len(self.scanner.networks) if self.scanner else 0
                }
            })
        except Exception as e:
            logger.error(f"Error getting scan status: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    # Attack endpoints implementation
    async def start_attack(self, request: web.Request) -> web.Response:
        """Start attack."""
        try:
            if not self.attack_manager:
                return web.json_response({
                    "success": False,
                    "error": "No adapter selected"
                }, status=400)

            data = await request.json()

            # Parse attack configuration
            attack_type_str = data.get('type', 'deauth')
            attack_type = AttackType(attack_type_str)

            config = AttackConfig(
                attack_type=attack_type,
                target_bssid=data['bssid'],
                target_channel=data['channel'],
                packet_count=data.get('packet_count', 100),
                delay_ms=data.get('delay_ms', 100),
                client_mac=data.get('client_mac'),
                continuous=data.get('continuous', False)
            )

            # Progress callback
            def on_progress(sent, total):
                asyncio.create_task(self.ws_manager.broadcast({
                    "type": "attack_progress",
                    "data": {"sent": sent, "total": total}
                }))

            # Start attack in background
            asyncio.create_task(asyncio.to_thread(
                self.attack_manager.start_attack,
                config=config,
                progress_callback=on_progress
            ))

            self.is_attacking = True

            return web.json_response({
                "success": True,
                "message": "Attack started"
            })
        except Exception as e:
            logger.error(f"Error starting attack: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def stop_attack(self, request: web.Request) -> web.Response:
        """Stop attack."""
        try:
            if self.attack_manager:
                self.attack_manager.stop_attack()
                self.is_attacking = False

            return web.json_response({
                "success": True,
                "message": "Attack stopped"
            })
        except Exception as e:
            logger.error(f"Error stopping attack: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def get_attack_status(self, request: web.Request) -> web.Response:
        """Get attack status."""
        try:
            if not self.attack_manager:
                return web.json_response({
                    "success": True,
                    "data": {"is_attacking": False, "packets_sent": 0}
                })

            packets_sent, is_attacking = self.attack_manager.get_progress()
            return web.json_response({
                "success": True,
                "data": {
                    "is_attacking": is_attacking,
                    "packets_sent": packets_sent
                }
            })
        except Exception as e:
            logger.error(f"Error getting attack status: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    # Configuration endpoints implementation
    async def get_config(self, request: web.Request) -> web.Response:
        """Get configuration."""
        try:
            return web.json_response({
                "success": True,
                "data": self.config.to_dict()
            })
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def update_config(self, request: web.Request) -> web.Response:
        """Update configuration."""
        try:
            data = await request.json()
            section = data.get('section')
            values = data.get('values', {})

            if section:
                self.config.update(section, **values)

            return web.json_response({
                "success": True,
                "message": "Configuration updated"
            })
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def reset_config(self, request: web.Request) -> web.Response:
        """Reset configuration."""
        try:
            self.config.reset()
            return web.json_response({
                "success": True,
                "message": "Configuration reset to defaults"
            })
        except Exception as e:
            logger.error(f"Error resetting config: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    def run(self) -> None:
        """Run the API server."""
        host = self.config.server.host
        port = self.config.server.port
        
        logger.info(f"Starting WIFIjam API server on {host}:{port}")
        web.run_app(self.app, host=host, port=port)

