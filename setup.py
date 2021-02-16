""" Setup file for intelmq-api

SPDX-FileCopyrightText: 2020 Birger Schacht
SPDX-License-Identifier: AGPL-3.0-or-later
"""
import setuptools

from intelmq_api.version import __version__

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="intelmq-api",
    version=__version__,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/certtools/intelmq-api",
    packages=setuptools.find_packages(),
    install_requires=[
        "hug>=2.3.0",
        "intelmq>=2.2.3",
    ],
    python_requires='>=3.6',
    description="Intelmq-API is a hug based API to intelmq,"
                " a solution for IT security teams for collecting"
                " and processing security feeds",
    data_files=[('/etc/intelmq', ['contrib/api-config.json', 'contrib/api-apache.conf', 'contrib/api-sudoers.conf']),
                ('/etc/intelmq/manager', ['contrib/positions.conf'])],
    package_data={'intelmq_api': ['intelmq-api.wsgi']},
    scripts = ['scripts/intelmq-api-adduser']
)
