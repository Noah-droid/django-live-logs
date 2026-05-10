from setuptools import setup, find_packages

setup(
    name="django-live-logs",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2",
        "channels>=4.0",
    ],
    author="Your Name",
    description="A standalone Django package to stream logs over WebSockets.",
)
