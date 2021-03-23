.. 
   SPDX-FileCopyrightText: 2020 Birger Schacht
   SPDX-License-Identifier: AGPL-3.0-or-later

CHANGELOG
=========


3.0.0 (unreleased)
------------------

The API endpoint ``/api/config`` no longer provides the ``BOTS`` file, as it was removed from IntelMQ. The new endpoint ``/api/bots`` provides the same information.


2.3.0 (2021-03-04)
------------------

This is the first release as separate project. ``intelmq-api`` has been a part of ``intelmq-manager`` but has now been turned into its own project.
It is based on ``intelmq-manager``'s commit ``829f8cf7aeda6f455e4085a69bde297015e5d0a5`` from November 2020.
