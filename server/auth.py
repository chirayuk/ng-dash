# -*- coding: utf-8 -*-

from google.appengine.api import users

import Crypto
from Crypto import Random

import endpoints

from . import models
from . import utils


ALLOWED_CLIENT_IDS = [
  endpoints.API_EXPLORER_CLIENT_ID,
  "731555738015-hna1v9or40ml5saoqh0b87t3j6fh6juv.apps.googleusercontent.com",
  "731555738015-jstpm0j9hcsv266fnj098q897n3bcifb.apps.googleusercontent.com",
]

ADMIN_USER_EMAILS = set((
  "chirayuk@gmail.com", "chirayu@chirayuk.com", "chirayu@google.com",
))


def ensure_endpoints_user_is_admin():
  current_user = endpoints.get_current_user()
  if current_user is None:
    raise endpoints.UnauthorizedException('Invalid token.')
  if current_user.email() not in ADMIN_USER_EMAILS:
    raise endpoints.UnauthorizedException('Not an admin user.')


def create_secret_token():
  secret_bytes = Random.get_random_bytes(32)
  # TODO
  # get rsa key and sign it
  # return secret_bytes and signature as one string.
