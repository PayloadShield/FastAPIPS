"""
Setup configuration for fastapi_payloadshield package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastapi_payloadshield",
    version="3.0.0",
    author="Ganesh Kandu",
    author_email="kanduganesh@gmail.com",
    description="Pluggable FastAPI decorators for encrypting/decrypting request and response payloads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PayloadShield/FastAPIPS",
    packages=find_packages(),
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.7",
    install_requires=[
        "fastapi>=0.68.0",
        "starlette>=0.19.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
        ],
    },
)
