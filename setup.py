import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="replit-play",
    version="0.0.22",
    description="The easiest way to make games and media projects in Python.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/replit/play",
    author="Repl.it",
    author_email="gchiacchieri@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.5",
    packages=["play"],
    include_package_data=True,
    install_requires=["pygame", "numpy", "pymunk"],
)
