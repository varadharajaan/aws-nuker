"""Setup configuration for AWS Nuker."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="aws-nuker",
    version="1.0.0",
    author="AWS Nuker Team",
    description="A comprehensive AWS resource cleanup tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/varadharajaan/aws-nuker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.34.0",
        "botocore>=1.34.0",
        "colorama>=0.4.6",
        "python-dateutil>=2.8.2",
        "PyYAML>=6.0.1",
        "tabulate>=0.9.0",
        "tqdm>=4.66.0",
        "click>=8.1.7",
    ],
    entry_points={
        "console_scripts": [
            "aws-nuker=aws_nuker.cli:main",
        ],
    },
)
