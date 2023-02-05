import pathlib
from setuptools import setup, find_packages


setup(
    name="o2h",
    version="1.1.0",
    author="Chivier Humber",
    long_description_content_type="text/markdown",
    url="https://github.com/Chivier/H2O2H",
    long_description="# README\n",
    entry_points={
        "console_scripts": ["obs2hexo=o2h.o2h:o2h"],
    },
    license="MIT",
    keywords="translator",
    packages=find_packages(),
)
