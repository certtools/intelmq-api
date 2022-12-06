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
import os
import pathlib
import string
import typing

from fastapi import (Depends, FastAPI, Header, HTTPException, Request,
                     Response, status)
from fastapi.responses import JSONResponse
from intelmq.lib import utils  # type: ignore
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing_extensions import Literal  # Python 3.8+

import intelmq_api.config
import intelmq_api.files as files
import intelmq_api.runctl as runctl
import intelmq_api.session as session

app = FastAPI()  # TODO: use blueprints?


Levels = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "ALL"]
Actions = Literal["start", "stop", "restart", "reload", "status"]
Groups = Literal["collectors", "parsers", "experts", "outputs", "botnet"]
BotCmds = Literal["get", "pop", "send", "process"]
Pages = Literal["configs", "management", "monitor", "check", "about", "index"]

ID_CHARS = set(string.ascii_letters + string.digits + "-")


def ID(id: str) -> str:
    if not set(id) < ID_CHARS:
        raise ValueError("Invalid character in {!r}".format(id))
    return id


T = typing.TypeVar("T")


class OneTimeDependency(typing.Generic[T]):
    """Allows one-time explicit initialization of the dependency, 
        and then returning it on every usage.

        It emulates the previous behavior that used global variables"""

    def __init__(self) -> None:
        self._value: typing.Optional[T] = None

    def initialize(self, value: T) -> None:
        self._value = value

    def __call__(self) -> typing.Optional[T]:
        return self._value


api_config = OneTimeDependency[intelmq_api.config.Config]()
session_store = OneTimeDependency[session.SessionStore]()


def runner(config: intelmq_api.config.Config = Depends(api_config)):
    return runctl.RunIntelMQCtl(config.intelmq_ctl_cmd)


def file_access(config: intelmq_api.config.Config = Depends(api_config)):
    return files.FileAccess(config)


@app.on_event("startup")
def startup_event():
    config = intelmq_api.config.Config(os.environ.get("INTELMQ_API_CONFIG"))
    api_config.initialize(config)
    session_file = config.session_store
    if session_file is not None:
        session_store.initialize(session.SessionStore(str(session_file),
                                                      config.session_duration))


def cached_response(max_age: int):
    """Adds the cache headers to the response"""
    def _cached_response(response: Response):
        response.headers["cache-control"] = f"max-age={max_age}"
    return _cached_response


cached = Depends(cached_response(max_age=3))


@app.exception_handler(runctl.IntelMQCtlError)
def crl_error_handler(request: Request, exc: runctl.IntelMQCtlError):
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=exc.error_dict)


@app.exception_handler(StarletteHTTPException)
def handle_generic_error(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# TODO: go back to the original header
def token_authorization(auth: typing.Union[str, None] = Header(default=None),
                        session: session.SessionStore = Depends(session_store)):
    if session is not None:
        if not auth or not session.verify_token(auth):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")


authorized = Depends(token_authorization)


@app.get("/api/botnet", dependencies=[authorized])
def botnet(action: Actions, group: typing.Optional[Groups] = None, runner: runctl.RunIntelMQCtl = Depends(runner)):
    return runner.botnet(action, group)


@app.get("/api/bot", dependencies=[authorized])
def bot(action: Actions, id: str = Depends(ID), runner: runctl.RunIntelMQCtl = Depends(runner)):
    return runner.bot(action, id)


@app.get("/api/getlog", dependencies=[authorized, cached])
def get_log(lines: int, id: str = Depends(ID), level: Levels = "DEBUG", runner: runctl.RunIntelMQCtl = Depends(runner)):
    return runner.log(id, lines, level)


@app.get("/api/queues", dependencies=[authorized, cached])
def queues(runner: runctl.RunIntelMQCtl = Depends(runner)):
    return runner.list("queues")


@app.get("/api/queues-and-status", dependencies=[authorized, cached])
def queues_and_status(runner: runctl.RunIntelMQCtl = Depends(runner)):
    return runner.list("queues-and-status")


@app.get("/api/bots", dependencies=[authorized, cached])
def bots(runner: runctl.RunIntelMQCtl = Depends(runner)):
    return runner.list("bots")


@app.get("/api/version", dependencies=[authorized], response_model=typing.Dict)
def version(runner: runctl.RunIntelMQCtl = Depends(runner)):
    return runner.version()


@app.get("/api/check", dependencies=[authorized])
def check(runner: runctl.RunIntelMQCtl = Depends(runner)):
    return runner.check()


@app.get("/api/clear", dependencies=[authorized])
def clear(id: str = Depends(ID), runner: runctl.RunIntelMQCtl = Depends(runner)):
    return runner.clear(id)


# TODO: Model!
@app.post("/api/run", dependencies=[authorized], response_model=str)
def run(bot: str, cmd: BotCmds, show: bool = False, dry: bool = False,
        msg: str = "", runner: runctl.RunIntelMQCtl = Depends(runner)):
    return runner.run(bot, cmd, show, dry, msg)


@app.get("/api/debug", dependencies=[authorized])
def debug(runner: runctl.RunIntelMQCtl = Depends(runner)):
    return runner.debug()


@app.get("/api/config", dependencies=[authorized])
def config(response: Response, file: str, fetch: bool = False,
           file_access: files.FileAccess = Depends(file_access)):
    result = file_access.load_file_or_directory(file, fetch)
    if result is None:
        return ["Unknown resource"]

    content_type, contents = result
    response.headers["content-type"] = content_type
    return contents


class LoginForm(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    login_token: str
    username: str


@app.post("/api/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
def login(login_form: LoginForm, session: session.SessionStore = Depends(session_store)):
    username, password = login_form.username, login_form.password
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session store is disabled by configuration! No login possible and required.",
        )
    else:
        known = session.verify_user(username, password)
        if known is not None:
            token = session.new_session({"username": username})
            return {"login_token": token,
                    "username": username,
                    }
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid username and/or password.")


@app.get("/api/harmonization", dependencies=[authorized], response_model=typing.Dict)
def get_harmonization(runner: runctl.RunIntelMQCtl = Depends(runner)):
    harmonization = pathlib.Path('/opt/intelmq/etc/harmonization.conf')
    paths = runner.get_paths()
    if 'CONFIG_DIR' in paths:
        harmonization = pathlib.Path(paths['CONFIG_DIR']) / 'harmonization.conf'
    try:
        return json.loads(harmonization.read_text())
    except OSError as e:
        print(f"Could not read {harmonization}: {str(e)}")
        return {}


@app.get("/api/runtime", dependencies=[authorized], response_model=typing.Dict)
def get_runtime():
    return utils.get_runtime()


@app.post("/api/runtime", dependencies=[authorized], response_model=str)
def post_runtime(body: dict):
    try:
        utils.set_runtime(body)
        return "success"
    except Exception as e:
        print(f"Could not write runtime {str(e)}")
        return str(e)


@app.get("/api/positions", dependencies=[authorized], response_model=typing.Dict)
def get_positions(runner: runctl.RunIntelMQCtl = Depends(runner)):
    positions = pathlib.Path('/opt/intelmq/etc/manager/positions.conf')
    paths = runner.get_paths()
    if 'CONFIG_DIR' in paths:
        positions = pathlib.Path(paths['CONFIG_DIR']) / 'manager/positions.conf'
    try:
        return json.loads(positions.read_text())
    except OSError as e:
        print(f"Could not read {positions}: {str(e)}")
        return {}


@app.post("/api/positions", dependencies=[authorized], response_model=typing.Dict)
def post_positions(body: dict, runner: runctl.RunIntelMQCtl = Depends(runner)):
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
