from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="studybuddy",
    version="0.1",
    author="daud1",
    packages=find_packages(),
    install_requires=requirements,
)
