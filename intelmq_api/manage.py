"""
SPDX-FileCopyrightText: 2022 CERT.at GmbH <https://cert.at>
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import getpass
import sys
from typing import Optional

import intelmq_api.api
import intelmq_api.config
import intelmq_api.session

from pprint import pprint

import typer

from .main import config as api_config

cli = typer.Typer()


@cli.command()
def add_user(username: str, password: Optional[str] = None):
    if api_config.session_store is None:
        print("No session store configured in configuration!", file=sys.stderr)
        exit(1)

    session_store = intelmq_api.session.SessionStore(str(api_config.session_store),
                                                     api_config.session_duration)

    if password is None:
        password = getpass.getpass()
    session_store.add_user(username, password)


@cli.command()
def print_config():
    all_confs = {**intelmq_api.config.Config.__dict__, **api_config.__dict__}
    pprint({k: v for k, v in all_confs.items() if not k.startswith("_")})


if __name__ == "__main__":
    cli()
