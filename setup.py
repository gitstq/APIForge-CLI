#!/usr/bin/env python3
"""
Setup script for APIForge
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

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
    name="apiforge",
    version="1.0.0",
    description="🚀 AI-Powered API Mocking & Testing Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GitHub Incubator",
    author_email="agent@github-孵化器.ai",
    url="https://github.com/gitstq/APIForge",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "apiforge=apiforge.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.8",
    keywords="api mock testing http server development testing-toolkit",
    project_urls={
        "Bug Reports": "https://github.com/gitstq/APIForge/issues",
        "Source": "https://github.com/gitstq/APIForge",
        "Documentation": "https://github.com/gitstq/APIForge#readme",
    },
)
