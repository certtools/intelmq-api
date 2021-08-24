"""HTTP-API backend of IntelMQ-Manager

SPDX-FileCopyrightText: 2020 Intevation GmbH <https://intevation.de>
SPDX-License-Identifier: AGPL-3.0-or-later

Funding: of initial version by SUNET
Author(s):
  * Bernhard Herzog <bernhard.herzog@intevation.de>

This module implements the HTTP part of the API backend of
IntelMQ-Manager. The logic itself is in the runctl & files modules.
"""

import json
import sys
import os
import pathlib
import string
import typing

import hug  # type: ignore

import intelmq_api.runctl as runctl
import intelmq_api.files as files
import intelmq_api.config
import intelmq_api.session as session

from intelmq.lib import utils  # type: ignore

Levels = hug.types.OneOf(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL",
                          "ALL"])
Actions = hug.types.OneOf(["start", "stop", "restart", "reload", "status"])
Groups = hug.types.OneOf(["collectors", "parsers", "experts", "outputs",
                          "botnet"])
BotCmds = hug.types.OneOf(["get", "pop", "send", "process"])
Bool = hug.types.Mapping({"true": True, "false": False})
Pages = hug.types.OneOf(["configs", "management", "monitor", "check", "about",
                         "index"])


ID_CHARS = set(string.ascii_letters + string.digits + "-")
@hug.type(extend=hug.types.Text)
def ID(value):
    if not set(value) < ID_CHARS:
        raise ValueError("Invalid character in {!r}".format(value))
    return value


api_config: intelmq_api.config.Config

runner: runctl.RunIntelMQCtl

file_access: files.FileAccess


session_store = None


def initialize_api(config: intelmq_api.config.Config) -> None:
    """Initialize the API, optionally loading a configuration file.

    If a filename is given, this function updates the configuration in
    the module global variable api_config by loading a new configuration
    and assigning it to the variable.

    Then, regardless of whether a filename was given, it calls the
    update_from_runctl method of the file_access object so that it uses
    the files that IntelMQ actually uses.

    Note: Because of that last step this function should always be
    called when the server process starts even when no configuration
    needs to be read from a file.
    """
    global api_config, file_access, runner, session_store
    api_config = config

    runner = runctl.RunIntelMQCtl(api_config.intelmq_ctl_cmd)
    file_access = files.FileAccess(api_config)

    session_file = api_config.session_store
    if session_file is not None:
        session_store = session.SessionStore(str(session_file),
                                             api_config.session_duration)


def cache_get(*args, **kw):
    """Route to use instead of hug.get that sets cache headers in the response.
    """
    return hug.get(*args, **kw).cache(max_age=3)


@hug.exception(runctl.IntelMQCtlError)
def crlerror_handler(response, exception):
    response.status = hug.HTTP_500
    return exception.error_dict


def verify_token(token):
    if session_store is not None:
        return session_store.verify_token(token)
    else:
        return None

hug_token_authentication = hug.authentication.token(verify_token)

def token_authentication(*args, **kw):
    if session_store is not None:
        return hug_token_authentication(*args, **kw)
    else:
        return True


@hug.get("/api/botnet", requires=token_authentication, versions=1)
@typing.no_type_check
def botnet(action: Actions, group: Groups = None):
    return runner.botnet(action, group)


@hug.get("/api/bot", requires=token_authentication, versions=1)
@typing.no_type_check
def bot(action: Actions, id: ID):
    return runner.bot(action, id)


@cache_get("/api/getlog", requires=token_authentication, versions=1)
@typing.no_type_check
def getlog(id: ID, lines: int, level: Levels = "DEBUG"):
    return runner.log(id, lines, level)


@cache_get("/api/queues", requires=token_authentication, versions=1)
def queues():
    return runner.list("queues")


@cache_get("/api/queues-and-status", requires=token_authentication, versions=1)
def queues_and_status():
    return runner.list("queues-and-status")


@cache_get("/api/bots", requires=token_authentication, versions=1)
def bots():
    return runner.list("bots")


@hug.get("/api/version", requires=token_authentication, versions=1)
def version(request):
    return runner.version()


@hug.get("/api/check", requires=token_authentication, versions=1)
def check():
    return runner.check()


@hug.get("/api/clear", requires=token_authentication, versions=1)
@typing.no_type_check
def clear(id: ID):
    return runner.clear(id)


@hug.post("/api/run", requires=token_authentication, versions=1)
@typing.no_type_check
def run(bot: str, cmd: BotCmds, show: Bool = False, dry: Bool = False,
        msg: str = ""):
    return runner.run(bot, cmd, show, dry, msg)


@hug.get("/api/debug", requires=token_authentication, versions=1)
def debug():
    return runner.debug()


@hug.get("/api/config", requires=token_authentication, versions=1)
def config(response, file: str, fetch: bool=False):
    global file_access
    result = file_access.load_file_or_directory(file, fetch)
    if result is None:
        return ["Unknown resource"]

    content_type, contents = result
    response.content_type = content_type
    return contents


@hug.post("/api/login", versions=1)
def login(username: str, password: str):
    if session_store is None:
        return {"error": "Session store is disabled by configuration! No login possible and required."}
    else:
        known = session_store.verify_user(username, password)
        if known is not None:
            token = session_store.new_session({"username": username})
            return {"login_token": token,
                    "username": username,
                    }
        else:
            return {"error": "Invalid username and/or password."}


@hug.get("/api/harmonization", requires=token_authentication, versions=1)
def get_harmonization():
    harmonization = pathlib.Path('/opt/intelmq/etc/harmonization.conf')
    paths = runner.get_paths()
    if 'CONFIG_DIR' in paths:
        harmonization = pathlib.Path(paths['CONFIG_DIR']) / 'harmonization.conf'
    try:
        return json.loads(harmonization.read_text())
    except OSError as e:
        print(f"Could not read {harmonization}: {str(e)}")
        return {}


@hug.get("/api/runtime", requires=token_authentication, versions=1)
def get_runtime():
    return utils.get_runtime()


@hug.post("/api/runtime", requires=token_authentication, version=1)
def post_runtime(body):
    try:
        utils.set_runtime(body)
        return "success"
    except Exception as e:
        print(f"Could not write runtime {str(e)}")
        return str(e)


@hug.get("/api/positions", requires=token_authentication, versions=1)
def get_positions():
    positions = pathlib.Path('/opt/intelmq/etc/manager/positions.conf')
    paths = runner.get_paths()
    if 'CONFIG_DIR' in paths:
        positions = pathlib.Path(paths['CONFIG_DIR']) / 'manager/positions.conf'
    try:
        return json.loads(positions.read_text())
    except OSError as e:
        print(f"Could not read {positions}: {str(e)}")
        return {}


@hug.post("/api/positions", requires=token_authentication, version=1)
def post_positions(body):
    positions = pathlib.Path('/opt/intelmq/etc/manager/positions.conf')
    paths = runner.get_paths()
    if 'CONFIG_DIR' in paths:
        positions = pathlib.Path(paths['CONFIG_DIR']) / 'manager/positions.conf'
    try:
        positions.parent.mkdir(exist_ok=True)
        positions.write_text(json.dumps(body, indent=4))
        return "success"
    except OSError as e:
        print(f"Error creating {positions.parent} or writing to {positions}: {str(e)}")
        return str(e)
