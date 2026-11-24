"""
TerraDesk setup.py
"""

from setuptools import setup, find_packages

setup(
    name="tetradesk",
    version="1.0.0",
    description="TerraDesk - Desktop Village Simulation",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pygame-ce>=2.5.0",
        "pywin32>=305; sys_platform == 'win32'",
    ],
    extras_require={
        "build": ["pyinstaller>=6.0"],
    },
    entry_points={
        "console_scripts": [
            "tetradesk=main:main",
        ],
    },
)