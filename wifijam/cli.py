"""
Command-line interface for WIFIjam.
Provides CLI commands for running the application.
"""

import sys
import argparse
import webbrowser
from pathlib import Path

from wifijam import __version__, logger
from wifijam.core.config import Config
from wifijam.core.system import get_system_detector
from wifijam.api.server import APIServer


def print_banner():
    """Print application banner."""
    banner = f"""
╦ ╦╦╔═╗╦ ╦┌─┐┌┬┐
║║║║╠╣ ║ ║├─┤│││
╚╩╝╩╚  ╩ ╩┴ ┴┴ ┴
WiFi Security Testing Tool v{__version__}
By Vivek W (AryanVBW)
"""
    print(banner)


def cmd_gui(args):
    """Start GUI mode (API server + dashboard)."""
    print_banner()
    
    # Load configuration
    config = Config()
    
    # Check system
    system = get_system_detector()
    logger.info(f"Running on {system.system_info.os_name} {system.system_info.os_version}")
    
    if not system.system_info.is_root:
        logger.warning("Not running as root. Some features may not work.")
        logger.warning("Run with sudo for full functionality.")
    
    # Start API server
    logger.info("Starting WIFIjam in GUI mode...")
    server = APIServer(config)
    
    # Open browser
    if not args.no_browser:
        url = f"http://{config.server.host}:{config.server.port}"
        logger.info(f"Opening dashboard at {url}")
        webbrowser.open(url)
    
    # Run server
    server.run()


def cmd_info(args):
    """Display system information."""
    print_banner()
    
    system = get_system_detector()
    info = system.get_info_dict()
    
    print("\n=== System Information ===")
    print(f"OS: {info['os_name']} {info['os_version']}")
    print(f"Architecture: {info['architecture']}")
    print(f"Hostname: {info['hostname']}")
    print(f"Python: {info['python_version']}")
    print(f"Root/Admin: {'Yes' if info['is_root'] else 'No'}")
    
    print("\n=== Capabilities ===")
    print(f"Monitor Mode Support: {'Yes' if info['has_monitor_mode_support'] else 'No'}")
    print(f"Packet Injection Support: {'Yes' if info['has_packet_injection_support'] else 'No'}")
    
    print("\n=== Dependencies ===")
    for dep, available in info['dependencies'].items():
        status = "✓" if available else "✗"
        print(f"{status} {dep}")
    
    print()


def cmd_adapters(args):
    """List WiFi adapters."""
    print_banner()
    
    from wifijam.wifi.adapter import AdapterManager
    
    manager = AdapterManager()
    adapters = manager.adapters
    
    if not adapters:
        print("No WiFi adapters found.")
        return
    
    print(f"\n=== WiFi Adapters ({len(adapters)}) ===\n")
    
    for i, adapter in enumerate(adapters, 1):
        print(f"{i}. {adapter.interface}")
        print(f"   Name: {adapter.name}")
        if adapter.mac_address:
            print(f"   MAC: {adapter.mac_address}")
        if adapter.driver:
            print(f"   Driver: {adapter.driver}")
        print(f"   Status: {'UP' if adapter.is_up else 'DOWN'}")
        print(f"   Monitor Mode: {'Enabled' if adapter.is_monitor_mode else 'Disabled'}")
        if adapter.capabilities:
            caps = ", ".join([cap.value for cap in adapter.capabilities])
            print(f"   Capabilities: {caps}")
        print()


def cmd_config(args):
    """Manage configuration."""
    config = Config()
    
    if args.show:
        print("\n=== Current Configuration ===\n")
        import json
        print(json.dumps(config.to_dict(), indent=2))
    
    elif args.reset:
        config.reset()
        print("Configuration reset to defaults.")
    
    elif args.set:
        section, key_value = args.set.split('.', 1)
        key, value = key_value.split('=', 1)
        
        # Parse value
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        
        config.update(section, **{key: value})
        print(f"Configuration updated: {section}.{key} = {value}")


def cmd_version(args):
    """Display version information."""
    print(f"WIFIjam version {__version__}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="WIFIjam - WiFi Security Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'WIFIjam {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # GUI command
    gui_parser = subparsers.add_parser('gui', help='Start GUI mode (default)')
    gui_parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open browser automatically'
    )
    gui_parser.set_defaults(func=cmd_gui)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Display system information')
    info_parser.set_defaults(func=cmd_info)
    
    # Adapters command
    adapters_parser = subparsers.add_parser('adapters', help='List WiFi adapters')
    adapters_parser.set_defaults(func=cmd_adapters)
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_group = config_parser.add_mutually_exclusive_group()
    config_group.add_argument('--show', action='store_true', help='Show current configuration')
    config_group.add_argument('--reset', action='store_true', help='Reset to defaults')
    config_group.add_argument('--set', metavar='SECTION.KEY=VALUE', help='Set configuration value')
    config_parser.set_defaults(func=cmd_config)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Default to GUI if no command specified
    if not args.command:
        args.command = 'gui'
        args.no_browser = False
        args.func = cmd_gui
    
    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

