# -*- coding: utf-8 -*-
"""Implementation of /api/run that can be used to expose either a RESTful
service or an endpoints service.

This module exposes a top level object, run_info_handler, which is suitable for
wrapping with a rest_handler.RestProtoJsonRoute adapter to convert it to a
webapp2 Route.  run_info_handler exposes handlers to manipulate the
RunInfoModel model in the datastore.
"""

from google.appengine.api import users

from . import models
from . import utils


def get_all():
  return [terms_item.msg for terms_item
          in models.RunInfoModel.query_all()]


def get_by_commit_sha(commit_sha):
  return [terms_item.msg for terms_item
          in models.RunInfoModel.query_by_sha(commit_sha)]


def get_by_id(id):
  result = models.RunInfoModel.Get(id)
  return None if result is None else result.msg


class RunInfoHandler(object):
  def Get(self, id=None, commit_sha=None):
    if id:
      return get_by_id(id)
    elif commit_sha:
      return get_by_commit_sha(commit_sha)
    else:
      return get_all()

  def get_by_commit_sha(self, commit_sha):
    return get_by_commit_sha(commit_sha)

  def Create(self, msg):
    msg.creation_timestamp = utils.TimestampUtcNow()
    current_user = users.get_current_user()
    if current_user:
      msg.creator_email = current_user.email()
    run_info_model = models.RunInfoModel(msg=msg)
    run_info_model.put()
    msg.id = str(run_info_model.key.id())
    return msg

  def Set(self, msg, id):
    run_info_model = models.RunInfoModel.Get(id)
    for name in models.RunInfoUserFields:
      setattr(run_info_model.msg, name, getattr(msg, name))
    run_info_model.put()
    return run_info_model.msg

run_info_handler = RunInfoHandler()
