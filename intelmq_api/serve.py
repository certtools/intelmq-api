"""Stand-alone server for IntelMQ-Manager

SPDX-FileCopyrightText: 2020 Intevation GmbH <https://intevation.de>
SPDX-License-Identifier: AGPL-3.0-or-later

Funding: of initial version by SUNET
Author(s):
  * Bernhard Herzog <bernhard.herzog@intevation.de>

This is the main entry point when serving all of the IntelMQ-Manager via
hug. In addition to the backend implemented in intelmq_api.api, this
module also serves the static files (JS, CSS, etc.).

Run with hug from the shell as:
   hug -f intelmq_api/serve.py
"""

import getpass
import os
import sys

import hug # type: ignore

import intelmq_api.api
import intelmq_api.config
import intelmq_api.session

api_config: intelmq_api.config.Config = intelmq_api.config.Config(os.environ.get("INTELMQ_API_CONFIG"))

api = hug.API(__name__)
api.http.add_middleware(hug.middleware.CORSMiddleware(api, allow_origins=api_config.allow_origins))

@hug.extend_api()
def add_api():
    return [intelmq_api.api]


@hug.startup()
def setup(api):
    """Initialize the API when hug starts.

    This function calls initialize_api passing the value of the
    environment variable INTELMQ_API_CONFIG as the name of the
    configuration file.
    """
    intelmq_api.api.initialize_api(api_config)


@hug.cli()
def add_user(username: str, password: str = None):
    if api_config.session_store is None:
        print("No session store configured in configuration!", file=sys.stderr)
        exit(1)

    session_store = intelmq_api.session.SessionStore(str(api_config.session_store),
                                         api_config.session_duration)


    if password is None:
        password = getpass.getpass()
    session_store.add_user(username, password)
