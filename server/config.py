# -*- coding: utf-8 -*-

"""Runtime configuration.

  is_dev_server: True when running under local dev_appserver
"""

__author__ = "chirayu@chirayuk.com (Chirayu Krishnappa)"


import logging
import os

is_dev_server = os.environ.get("SERVER_SOFTWARE", "").startswith("Development/")

debug = is_dev_server
if debug:
  logging.getLogger().setLevel(logging.DEBUG)
