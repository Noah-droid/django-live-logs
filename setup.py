import os
from setuptools import setup, find_packages

# Read the README.md for PyPI description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="django-live-logs",
    version="0.1.6",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2",
        "channels>=4.0",
    ],
    author="Your Name",
    description="A standalone Django package to stream logs over WebSockets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
