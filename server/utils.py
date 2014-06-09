# -*- coding: utf-8 -*-
"""Utility functions.

  TimestampUtcNow: Integer UTC timestamp for the current time.
"""

import calendar
import datetime


def TimestampUtcNow():
  """Get current UTC timestamp.

  Returns:
    The current UTC timestamp as an integer.
  """
  return int(calendar.timegm(datetime.datetime.utcnow().utctimetuple()))
