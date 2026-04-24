"""setup.py for BBOverLoad."""

from pathlib import Path
from setuptools import setup, find_packages

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="bboverload",
    version="0.1.0",
    description="APK decompilation and recompilation toolkit for mobile games",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="dox121-pixel",
    url="https://github.com/dox121-pixel/BBOverLoad",
    license="MIT",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "bboverload=bboverload.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Disassemblers",
        "Topic :: Utilities",
    ],
)
