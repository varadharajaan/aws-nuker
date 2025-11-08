from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aws-nuker",
    version="1.0.0",
    author="AWS Nuker",
    description="AWS Resource Cleanup and Destroyer Tool - Ruthlessly delete all AWS resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/varadharajaan/aws-nuker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "boto3>=1.28.0",
        "botocore>=1.31.0",
        "click>=8.1.0",
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "aws-nuker=aws_nuker.cli:main",
        ],
    },
)
