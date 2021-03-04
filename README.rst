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


Extensive documentation regarding the installation, configuration and usage of the `intelmq-api` can be found in the `intelmq documentation <https://intelmq.readthedocs.io/en/maintenance/user/intelmq-api.html>`_.


*************
Type checking
*************

Except for the parts that directly deal with ``hug``, the code can be
typechecked with ``mypy``. To run the type checker, start with the module
``serve``:

.. code-block:: bash

   mypy intelmq_manager/serve.py
