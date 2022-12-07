.. 
   SPDX-FileCopyrightText: 2020-2022 Birger Schacht, Sebastian Wagner
   SPDX-License-Identifier: AGPL-3.0-or-later

CHANGELOG
=========

3.1.0 RC2 (unreleased)
----------------------

**Removed:**

- Removed support for Python 3.6.
- Removed duplication of the CLI commands. Adding users could be done now only by using `scripts/intelmq-api-adduser`

**Added:**

- Added code style checks to CI.
- Added interactive API documentation available at `/docs` endpoint.
- Added the line length limit in Python files as 100 chars.

**Changed:**

- The base API framework was changed from hug to the FastAPI. All endpoints were rewritten to use it
  and the structure of the files were changed to better align with the FastAPI concepts.
- The startup point of the application is now `intelmq_api.main:app`

**Known issues:**

- The packaging isn't yet prepared to work with FastAPI-based API.
- The recommended Apache configuration doesn't support the FastAPI-based version yet.
- The documentation is not updated yet.


3.1.0 RC (2022-08-02)
---------------------

No changes. Just keeping version numbers in sync.


3.0.1 (2021-09-02)
------------------
- Return a matching error message if the session storage is disabled and therefore a login is not possible (PR#36 by Sebastian Wagner, fixes #35).

Known issues
^^^^^^^^^^^^

- Monitor: Loading referenced configuration files causes 500 fails if file does not exist (#37).

3.0.0 (2021-07-07)
------------------

- The API endpoint ``/api/config`` no longer provides the ``BOTS`` file, as it was removed from IntelMQ. The new endpoint ``/api/bots`` provides the same information.
- Adapt the configuration file handling to IntelMQ 3.0 (PR#30 by Birger Schacht).
  In IntelMQ 3 the defaults.conf and the pipeline.conf were dropped,
  therefore access to those files via the API is not useful anymore.
  At the same time, the runtime.conf now includes pipeline configuration
  and is stored as a YAML file. Given those changes, the whole
  configuration file handling had to be rewritten: There are now 3 API
  endpoints:
  * ``/api/runtime`` to read (get) and write (post) the runtime configuration
  * ``/api/positions`` to read (get) and write (post) the positions configuration
  * ``/api/harmonization`` to read (get) the harmonization information
  Everything is still done using JSON objects, the conversion to YAML is
  done internally.
  The removal of the ``save_file`` method also includes the removal of some
  sanity checks that ran before the file was saved. Some of those should
  probably be part of intelmq itself (i.e. checking for allowed characters
  in bot names).
- fix json output and add error handling (PR#31 by Birger Schacht, fixes #14):
  Hug can not simply return a string that contains json. Therefore the
  content of the files first has to converted to a JSON object.
  This commit also implements simple error handling in case the files do
  not exists or can not be created.
- The version API-endpoint now correctly reports the version of IntelMQ API
  as ``intelmq-api``, not as ``intelmq-manager`` (by Sebastian Wagner).


2.3.1 (2021-03-25)
------------------

Session database permission errors: Catch the exception in the code and add a hint to check the permissions of both the file and the directory (PR#25 by Birger Schacht, fixes #23).


2.3.0 (2021-03-04)
------------------

This is the first release as separate project. ``intelmq-api`` has been a part of ``intelmq-manager`` but has now been turned into its own project.
It is based on ``intelmq-manager``'s commit ``829f8cf7aeda6f455e4085a69bde297015e5d0a5`` from November 2020.
