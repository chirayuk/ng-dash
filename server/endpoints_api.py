# -*- coding: utf-8 -*-
"""Google Cloud EndPoints API for RunInfo.

Exports a WSGI application to serve the Google Cloud Endpoints API for RunInfo.

  RunInfoApi: An Endpoint handler for manipulating RunInfo models in the backend
  wsgi_app: A WSGI application for the RunInfo API.
"""


from . import models
from . import run_info
import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote

package = "com.appspot.ng-dash"

ALLOWED_CLIENT_IDS = [
  endpoints.API_EXPLORER_CLIENT_ID,
  "731555738015-hna1v9or40ml5saoqh0b87t3j6fh6juv.apps.googleusercontent.com",
  "731555738015-jstpm0j9hcsv266fnj098q897n3bcifb.apps.googleusercontent.com",
]

ADMIN_USER_EMAILS = set((
  "chirayuk@gmail.com", "chirayu@chirayuk.com", "chirayu@google.com",
))


def _ensure_admin_user():
  current_user = endpoints.get_current_user()
  if current_user is None:
    raise endpoints.UnauthorizedException('Invalid token.')
  if current_user.email() not in ADMIN_USER_EMAILS:
    raise endpoints.UnauthorizedException('Not an admin user.')


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
          items=run_info_handler.GetByCommitSha(request.commit_sha))
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
                    allowed_client_ids=ALLOWED_CLIENT_IDS)
  def new_run(self, request):
    _ensure_admin_user()
    try:
      return run_info_handler.Create(request)
    except (IndexError, TypeError):
      raise endpoints.NotFoundException("RunInfo[id=%s] not found." %
                                        (request.id,))


wsgi_app = endpoints.api_server([api], restricted=False)
