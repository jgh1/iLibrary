from setuptools import find_packages, setup

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(  # Note: no 'setuptools.' prefix here
    name = "iLibrary",
    version = "0.0.3",
    author = "Andreas Legner",
    author_email = "iLibrary@legner.beer",
    description = "iLibrary - Tools for IBM i",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://legner.beer",
    project_urls = {
        "Bug Tracker": "https://legner.beer/bugs",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "app"},
    packages = find_packages(where="app"),
    python_requires = ">=3.6"
)