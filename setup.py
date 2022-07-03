import pathlib
from setuptools import setup, find_packages


setup(
    name="o2h",
    version="1.0.0",
    author="Chivier Humber",
    entry_points={
        "console_scripts": ["obs2hexo=o2h.o2h:o2h"],
    },
    license="MIT",
    keywords="translator",
    packages=find_packages(),
)
