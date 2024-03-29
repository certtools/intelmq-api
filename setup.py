""" Setup file for intelmq-api

SPDX-FileCopyrightText: 2020 Birger Schacht
SPDX-License-Identifier: AGPL-3.0-or-later
"""
import setuptools

from intelmq_api.version import __version__

with open("README.rst", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = [
    "intelmq>=2.2.3",
    "fastapi>=0.63.0",  # Newest version in the Debian 11 repository
    "uvicorn[standard]>=0.20.0",
    "typing-extensions>=3.10.0.0",
    "python-multipart",
]

DEV_TOOLS = [
    "pycodestyle>=2.10.0",
    "httpx",
]

setuptools.setup(
    name="intelmq-api",
    version=__version__,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/certtools/intelmq-api",
    packages=setuptools.find_packages(),
    install_requires=REQUIREMENTS,
    python_requires='>=3.7',
    extras_require={
        'dev': DEV_TOOLS,
    },
    description="Intelmq-API is a FastAPI based API to intelmq,"
                " a solution for IT security teams for collecting"
                " and processing security feeds",
    data_files=[('/etc/intelmq', ['contrib/api-config.json', 'contrib/api-apache.conf',
                                  'contrib/api-sudoers.conf', 'contrib/intelmq-api.service',
                                  'contrib/intelmq-api.socket']),
                ('/etc/intelmq/manager', ['contrib/positions.conf'])],
    scripts=['scripts/intelmq-api-adduser', 'scripts/intelmq-api-setup-systemd']
)
