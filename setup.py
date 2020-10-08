#!/usr/bin/env python3

from pathlib import Path

import setuptools

project_dir = Path(__file__).parent

setuptools.setup(
    name="3d-beacons-hub-api",
    version="1.0.0",
    description="A Python package which has utilities related to "
    "3d-Beacons Hub API.",
    # Allow UTF-8 characters in README with encoding argument.
    long_description=project_dir.joinpath("README.md").read_text(encoding="utf-8"),
    keywords=["python"],
    author="Sreenath Sasidharan Nair",
    url="https://github.com/3D-Beacons/3d-beacons-hub-api.git",
    packages=setuptools.find_packages(),
    # package_dir={"": "app"},
    # pip 9.0+ will inspect this field when installing to help users install a
    # compatible version of the library for their Python version.
    python_requires=">=3.7",
    # There are some peculiarities on how to include package data for source
    # distributions using setuptools. You also need to add entries for package
    # data to MANIFEST.in.
    # See https://stackoverflow.com/questions/7522250/
    include_package_data=True,
    # # This file is required to inform mypy that inline type hints are used.
    # #   See: https://mypy.readthedocs.io/en/stable/installed_packages.html
    # package_data={"": ["py.typed"]},
    # This is a trick to avoid duplicating dependencies between both setup.py and
    # requirements.txt.
    # requirements.txt must be included in MANIFEST.in for this to work.
    # It does not work for all types of dependencies (e.g. VCS dependencies).
    # For VCS dependencies, use pip >= 19 and the PEP 508 syntax.
    #   Example: 'requests @ git+https://github.com/requests/requests.git@branch_or_tag'
    #   See: https://github.com/pypa/pip/issues/6162
    install_requires=project_dir.joinpath("requirements.txt").read_text().split("\n"),
    zip_safe=False,
    license="Apache License 2.0",
    license_files=["LICENSE"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={"console_scripts": ["hubapi_cli=app.cli:main"]},
)
