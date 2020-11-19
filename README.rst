###########
intelmq-api
###########

intelmq-api is a `hug <http://hug.rest>`_ based API for the `intelmq <https://github.com/certtools/intelmq/>`_ project.

**********************************
Installing and running intelmq-api
**********************************

Install ``intelmq-api`` using your preferred package installation mechanism (``pip``, ``apt``, ``yum``, ``dnf``...).

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
the environment variable ``INTELMQ_MANAGER_CONFIG``. A sample configuration file ``intelmq-api-config.json`` is part of
the distribution, it is also listed here fore reference:

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

* ``intelmq_ctl_cmd``: the path to your ``intelmqctl`` command. If this is not set in a configuration file the default is used, which is ``sudo -u intelmq /usr/local/bin/intelmqctl``
* ``allowed_path``: intelmq-api allows acces to files in this path
* ``session_store``: this is an optional path to a sqlite database, which is used for sesssion storage and authentication. If it is not set (which is the default), no authentication is used!
* ``session_duration``: the maximal duration of a session, its 86400 seconds by default
* ``allow_origins``: a list of origins the responses of the API can be shared with. Allows every origin by default.
* ``html_dir``: the path to the html files of the ``intelmq-manager``. If this path exists it is served under the path ``/management``
