# -*- coding: utf-8 -*-

"""Exposed HTTP APIS: A RESTful API and a Google Cloud EndPoints API.
"""

from . import config
from . import models
from . import rest_handler
from . import run_info
import webapp2


from google.appengine.api import users


class CkckHandler(webapp2.RequestHandler):
  def get(self, **params):
    self.response.write(users.create_login_url("/"))


def GetWsgiApp():
  """Return the main WSGI application.

  Our WSGI app is a webapp2 WSGIApplication.
  We use our custom RestProtoJsonRoute adapter to allow us to write our REST
  handlers at a high level -  dealing only with typed input messages and
  returning a typed response message without having to worry about
  serializing/deserializing JSON.

  Returns:
    WSGI application.
  """
  RestProtoJsonRoute = rest_handler.RestProtoJsonRoute

  routes = [
      webapp2.Route('/ckck', handler=CkckHandler),
      RestProtoJsonRoute(r'/api/run/id=<id:\d+>',
                         methods=['GET', 'PUT'],
                         name='runsById',
                         request_type=models.RunInfo,
                         handler=run_info.run_info_handler,
                         defaults=dict(id=None)),
      RestProtoJsonRoute(r'/api/run/commit_sha=<commit_sha:\d+>',
                         methods=['GET'],
                         name='runsByCommitSha',
                         request_type=models.RunInfo,
                         handler=run_info.run_info_handler,
                         defaults=dict(commit_sha=None)),
      RestProtoJsonRoute(r'/api/run',
                         name='runs',
                         request_type=models.RunInfo,
                         handler=run_info.run_info_handler),
      ]
  return webapp2.WSGIApplication(routes, debug=config.debug)


# This is our main WSGI application.  It only handles the /api/ URLs.
wsgi_app = GetWsgiApp()
