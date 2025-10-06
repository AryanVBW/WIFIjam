"""
Tests for system detection module.
"""

import pytest
from wifijam.core.system import SystemDetector, OSType


def test_system_detector_init():
    """Test SystemDetector initialization."""
    detector = SystemDetector()
    assert detector is not None
    assert detector.os_type in [OSType.LINUX, OSType.MACOS, OSType.WINDOWS, OSType.UNKNOWN]


def test_system_info():
    """Test system information gathering."""
    detector = SystemDetector()
    info = detector.system_info
    
    assert info is not None
    assert info.os_name
    assert info.os_version
    assert info.architecture
    assert info.hostname
    assert info.python_version
    assert isinstance(info.is_root, bool)
    assert isinstance(info.has_monitor_mode_support, bool)
    assert isinstance(info.has_packet_injection_support, bool)


def test_get_info_dict():
    """Test system info dictionary conversion."""
    detector = SystemDetector()
    info_dict = detector.get_info_dict()
    
    assert isinstance(info_dict, dict)
    assert 'os_type' in info_dict
    assert 'os_name' in info_dict
    assert 'dependencies' in info_dict


def test_check_dependencies():
    """Test dependency checking."""
    detector = SystemDetector()
    deps = detector.check_dependencies()
    
    assert isinstance(deps, dict)
    # All values should be boolean
    for dep, available in deps.items():
        assert isinstance(available, bool)

