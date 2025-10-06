"""
Setup script for WIFIjam.
Enables pip installation: pip install wifijam
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="wifijam",
    version="2.0.0",
    author="Vivek W (AryanVBW)",
    author_email="vivek.aryanvbw@gmail.com",
    description="Professional WiFi Security Testing Tool with GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AryanVBW/WIFIjam",
    project_urls={
        "Bug Reports": "https://github.com/AryanVBW/WIFIjam/issues",
        "Source": "https://github.com/AryanVBW/WIFIjam",
        "Documentation": "https://github.com/AryanVBW/WIFIjam#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Web Environment",
        "Framework :: AsyncIO",
    ],
    keywords="wifi security testing penetration-testing deauth jamming network-security",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wifijam=wifijam.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "wifijam": [
            "*.html",
            "*.css",
            "*.js",
            "*.png",
            "*.jpg",
            "*.jpeg",
        ],
    },
    zip_safe=False,
    platforms=["Linux", "macOS", "Windows"],
)

