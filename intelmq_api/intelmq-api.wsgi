""" WSGI file for intelmq-api

SPDX-FileCopyrightText: 2020 Birger Schacht
SPDX-License-Identifier: AGPL-3.0-or-later
"""
import os

def application (environ, start_response):
   if 'INTELMQ_API_CONFIG' in environ:
       os.environ['INTELMQ_API_CONFIG'] = environ['INTELMQ_API_CONFIG']
   from intelmq_api.serve import __hug_wsgi__
   return __hug_wsgi__(environ, start_response)
