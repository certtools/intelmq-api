..
   SPDX-FileCopyrightText: 2020 Birger Schacht
   SPDX-License-Identifier: AGPL-3.0-or-later

###########
intelmq-api
###########

|Tests Status| |Package Status|

.. |Tests Status| image:: https://github.com/certtools/intelmq-api/actions/workflows/python-unittests.yml/badge.svg
   :target: https://github.com/certtools/intelmq-api/actions/workflows/python-unittests.yml

.. |Package Status| image:: https://github.com/certtools/intelmq-api/actions/workflows/debian-package.yml/badge.svg
   :target: https://github.com/certtools/intelmq-api/actions/workflows/debian-package.yml

intelmq-api is a `FastAPI <https://fastapi.tiangolo.com/>`_ based API for the `intelmq <https://github.com/certtools/intelmq/>`_ project.


Extensive documentation regarding the installation, configuration and usage of the `intelmq-api` can be found in the `intelmq documentation <https://intelmq.readthedocs.io/en/maintenance/user/intelmq-api.html>`_.

*****************
Development usage
*****************

You could create a preferred virtual environment, and then install the package using:

.. code-block:: bash

   pip install -e .

For development purposes, you can run the API using the `scripts/run_dev.sh` script. It serves the
API on the local `8000` port and watches for file changes, with the automated reloading on change.

The interactive documentation is served on the `/docs` endpoint.

To set the API configuration, please export the `INTELMQ_API_CONFIG` environment variable with path
to the JSON config file in the shell you want to use. For the config reference, please check the
`intelmq_api/config.py` and the example from `contrib/api-config.json`.

If you configured the session store, you will need to authorize every request. The `/v1/login`
returns the authorization token. You can use the following command to register the user:

.. code-block:: bash

   ./scripts/intelmq-api-adduser --user UserName

*************
Security note
*************

Please be careful when deploying the API. At the current stage, it is not designed to run on
publicly exposed endpoints without additional pre-cautions.

*************
Type checking
*************

The code can be typechecked with ``mypy``. To run the type checker, use:

.. code-block:: bash

   mypy intelmq_api/
