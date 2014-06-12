# -*- coding: utf-8 -*-
"""Google Cloud EndPoints API for RunInfo.

Exports a WSGI application to serve the Google Cloud Endpoints API for RunInfo.

  RunInfoApi: An Endpoint handler for manipulating RunInfo models in the backend
  wsgi_app: A WSGI application for the RunInfo API.
"""

from google.appengine.ext.ndb import Key


from . import auth
from . import models
from . import run_info

import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote

package = "com.appspot.ng-dash"


class Error(Exception):
  pass



api = endpoints.api(name="ngdash", version="v0.1")

run_info_handler = run_info.run_info_handler

@api.api_class(resource_name="run", path="run")
class RunInfoApi(remote.Service):
  @endpoints.method(message_types.VoidMessage, models.RunInfoCollection,
                    path="", http_method="GET",
                    name="listRuns",
                    )
  def list_runs(self, unused_request):
    return models.RunInfoCollection(items=run_info_handler.Get())

  SHA_PARAM_RESOURCE = endpoints.ResourceContainer(
      message_types.VoidMessage,
      commit_sha=messages.StringField(1))

  @endpoints.method(SHA_PARAM_RESOURCE, models.RunInfoCollection,
                    path="commit_sha/{commit_sha}", http_method="GET",
                    name="getRunBySha")
  def get_run_by_commit_sha(self, request):
    try:
      return models.RunInfoCollection(
          items=run_info_handler.get_by_commit_sha(request.commit_sha))
    except (IndexError, TypeError):
      raise endpoints.NotFoundException("RunInfo[commit_sha=%s] not found." %
                                        (request.commit_sha,))

  ID_PARAM_RESOURCE = endpoints.ResourceContainer(
      message_types.VoidMessage,
      id=messages.StringField(1))

  @endpoints.method(ID_PARAM_RESOURCE, models.RunInfo,
                    path="id/{id}", http_method="GET",
                    name="getRunById")
  def get_run_by_id(self, request):
    try:
      return run_info_handler.Get(request.id)
    except (IndexError, TypeError):
      raise endpoints.NotFoundException("RunInfo[id=%s] not found." %
                                        (request.id,))

  @endpoints.method(models.RunInfo, models.RunInfo,
                    path="new_run", http_method="POST",
                    name="newRun",
                    auth_level=endpoints.AUTH_LEVEL.REQUIRED,
                    allowed_client_ids=auth.ALLOWED_CLIENT_IDS)
  def new_run(self, request):
    auth.ensure_recognized_user()
    try:
      return run_info_handler.Create(request)
    except (IndexError, TypeError):
      raise endpoints.NotFoundException("RunInfo[id=%s] not found." %
                                        (request.id,))


auth_api = endpoints.api(name="ngdash_auth", version="v0.1",
                         auth_level=endpoints.AUTH_LEVEL.REQUIRED,
                         allowed_client_ids=auth.ALLOWED_CLIENT_IDS)


# This service should only be open to superadmins.  It allows you to create and
# reset admin users.
@auth_api.api_class(resource_name="auth", path="auth")
class AuthApi(remote.Service):
  @endpoints.method(models.ApiUser, models.ApiUser,
                    path="register_api_key", http_method="POST",
                    name="registerApiKey")
  def recreate_api_user(self, api_user):
    auth.ensure_recognized_user(require_admin=True)
    if not api_user.email:
      raise Error("recreate_api_user: E-mail cannot be blank")
    db_key = Key(models.ApiUserModel, api_user.email)
    api_user_model = db_key.get()
    if api_user_model:
      if (api_user.secret and
          api_user_model.msg.secret != api_user.secret):
        raise Error("Can't set a custom secret. If you want a new one, just clear it and the server will generate a new one for you.")
    else:
      api_user_model = models.ApiUserModel(msg=api_user)
      api_user_model.key = db_key
    secret = api_user.secret
    if not api_user.secret:
      print("ckck: temp new token=" + auth.create_secret_token())
      api_user_model.msg.secret = auth.create_secret_token()
      print("ckck: new secret = " + api_user_model.msg.secret)
    api_user_model.put()
    return api_user_model.msg



wsgi_app = endpoints.api_server([api, auth_api], restricted=False)
