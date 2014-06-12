# -*- coding: utf-8 -*-

import base64

from google.appengine.api import users
from google.appengine.ext.ndb import (
    BlobProperty,
    Key,
    Model,
    StringProperty,
)


import itsdangerous
from Crypto import Random

import endpoints

from . import models
from . import utils


ALLOWED_CLIENT_IDS = [
  endpoints.API_EXPLORER_CLIENT_ID,
  "731555738015-hna1v9or40ml5saoqh0b87t3j6fh6juv.apps.googleusercontent.com",
  "731555738015-jstpm0j9hcsv266fnj098q897n3bcifb.apps.googleusercontent.com",
]

SUPER_ADMIN_USER_EMAILS = set((
  "chirayuk@gmail.com", "chirayu@chirayuk.com", "chirayu@google.com",
))


class ApplicationPrivateKey(Model):
  # 20 bytes since this is used with SHA1 digests and larger is pointless.
  secret_bytes = BlobProperty()


APPLICATION_PRIVATE_KEY = None
SIGNER = None

def _get_app_private_key():
  global APPLICATION_PRIVATE_KEY
  if not APPLICATION_PRIVATE_KEY:
    db_key = Key(ApplicationPrivateKey, "PrivateKey")
    private_key = db_key.get()
    if private_key is None:
      private_key = ApplicationPrivateKey(
          secret_bytes=Random.get_random_bytes(20))
      private_key.key = db_key
      print("Storing a new private key in the datastore")
      private_key.put()
    APPLICATION_PRIVATE_KEY = private_key
  return APPLICATION_PRIVATE_KEY


def get_signer():
  global SIGNER
  if not SIGNER:
    SIGNER = itsdangerous.Signer(_get_app_private_key().secret_bytes)
  return SIGNER


def create_secret_token():
  secret_bytes = Random.get_random_bytes(20)
  return get_signer().sign(base64.b64encode(secret_bytes))


def get_api_user_by_cookies(request):
  # Try looking up cookies for secret/token.
  email = request.cookies.get('user_email')
  secret = request.cookies.get('user_secret')
  print("ckck: email={0}, secret={1}".format(email, secret))
  if not email or not secret:
    return False
  # HMAC check to prevent spamming the DB if someone is randomly hitting us
  # trying different cookies
  secret_bytes = get_signer().unsign(secret)
  api_user = models.ApiUserModel.get_by_email(email)
  if not api_user:
    return False
  if api_user.secret != secret:
    return False
  return api_user


def get_api_user(request=None, require_admin=False):
  try:
    current_user = endpoints.get_current_user()
    if current_user and current_user.email() in SUPER_ADMIN_USER_EMAILS:
      return models.ApiUser(email=current_user.email(),
                            is_admin=True)
  except endpoints.InvalidGetUserCall:
    pass
  if request:
    api_user = get_api_user_by_cookies(request)
    if api_user and (not require_admin or api_user.is_admin):
      print "Recognized api_user: email={0}, is_admin={1}, secret={2}".format(
          api_user.email, api_user.is_admin, api_user.secret)
      return api_user
  return None


def ensure_recognized_user(request=None, require_admin=False):
  user = get_api_user(request=request, require_admin=require_admin)
  if not user:
    raise endpoints.UnauthorizedException('Unknown user or user does not have access.')
  return user
