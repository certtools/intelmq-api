.. 
   SPDX-FileCopyrightText: 2020 Birger Schacht
   SPDX-License-Identifier: AGPL-3.0-or-later

###########
intelmq-api
###########

|Build Status|

.. |Build Status| image:: https://travis-ci.com/certtools/intelmq-api.svg?branch=develop
   :target: https://travis-ci.com/certtools/intelmq-api

intelmq-api is a `hug <http://hug.rest>`_ based API for the `intelmq <https://github.com/certtools/intelmq/>`_ project.

**********************************
Installing and running intelmq-api
**********************************

``intelmq-api`` requires at least `Python 3.6 <https://www.python.org/downloads/release/python-360/>`_.

Install ``intelmq-api`` using your preferred package installation mechanism (``pip``, ``apt``, ``yum``, ``dnf``...).

* ``pip install intelmq-api``
* ``apt install intelmq-api``
* ``yum install intelmq-api``
* ``zypper install intelmq-api``

Depending on your setup you might have to install ``sudo`` to make it possible for the ``intelmq-api`` to run the ``intelmq`` command as the user-account usually used to run ``intelmq`` (which is also often called ``intelmq``).

You can run ``intelmq-api`` directly using ``hug``:

.. code-block:: bash

   hug -m intelmq_api.serve


Or using uwsgi

.. code-block:: bash

   uwsgi --http 0.0.0.0:8000 -w intelmq_api.serve --callable __hug_wsgi__

Or using gunicorn

.. code-block:: bash

   gunicorn intelmq_api.serve:__hug_wsgi__


The ``intelmq-api`` provides the route ``/api`` for managing the ``intelmq`` installation. If it has access to an installation of the ``intelmq-manager`` files it serves them under the ``/management`` route.

***********************
Configuring intelmq-api
***********************

intelmq-api is configured using a configuration file in ``json`` format. The path to the configuration file is set using
the environment variable ``INTELMQ_MANAGER_CONFIG``. When running the API using ``hug``, you can set the environment
variable like this:

.. code-block:: bash

   INTELMQ_MANAGER_CONFIG=intelmq-api-config.json hug -m intelmq_api.serve


A sample configuration file ``intelmq-api-config.json`` is part of the distribution, it is also listed here fore reference.
In this configuration the setting ``session_store`` is disabled by prepending it with an underscore:

.. code-block:: json

   {
           "intelmq_ctl_cmd": ["intelmqctl"],
           "allowed_path": "/opt/intelmq/var/lib/bots/",
           "_session_store": "/tmp/intelmq-session.sqlite",
           "session_duration": 86400,
           "allow_origins": ["*"],
           "html_dir": "/usr/share/intelmq-manager/html/"
   }

The following configuration options are available:

* ``intelmq_ctl_cmd``: Your ``intelmqctl`` command. If this is not set in a configuration file the default is used, which is ``["sudo", "-u", "intelmq", "/usr/local/bin/intelmqctl"]``
   The option `"intelmq_ctl_cmd"` is a list of strings so that we can avoid shell-injection vulnerabilities because no shell is involved when running the command.
   This means that if the command you want to use needs parameters, they have to be separate strings.

* ``allowed_path``: intelmq-api can grant **read-only** access to specific files- this setting defines the path those files can reside in
* ``session_store``: this is an optional path to a sqlite database, which is used for sesssion storage and authentication. If it is not set (which is the default), no authentication is used!
* ``session_duration``: the maximal duration of a session, its 86400 seconds by default
* ``allow_origins``: a list of origins the responses of the API can be shared with. Allows every origin by default.
* ``html_dir``: the path to the html files of the ``intelmq-manager``. If this path exists it is served under the path ``/management``

*************
Adding a user
*************

If you set theh ``session_store`` configuration setting you have to create a user to be able to access the API functionality. You can do this also using hug:

.. code-block:: bash

   hug -m intelmq_api.serve -c add_user <username>

**************
Usual problems
**************

If the command is not configured correctly, you'll see exceptions on startup like this:

.. code-block:: bash

   intelmq_manager.runctl.IntelMQCtlError: <ERROR_MESSAGE>

This means the intelmqctl command could not be executed as a subprocess.
The ``<ERROR_MESSAGE>`` should indicate why.

To save the positions of the bots in the configuration map, you need
an existing writable ``manager/positions.conf`` file. If it's missing,
just create an empty one.

*************
Type checking
*************

Except for the parts that directly deal with ``hug``, the code can be
typechecked with ``mypy``. To run the type checker, start with the module
``serve``:

.. code-block:: bash

   mypy intelmq_manager/serve.py
