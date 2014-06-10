# -*- coding: utf-8 -*-
"""Implementation of /api/run that can be used to expose either a RESTful
service or an endpoints service.

This module exposes a top level object, run_info_handler, which is suitable for
wrapping with a rest_handler.RestProtoJsonRoute adapter to convert it to a
webapp2 Route.  run_info_handler exposes handlers to manipulate the
RunInfoModel model in the datastore.
"""

from . import models
from . import utils


def GetAll():
  return [terms_item.msg for terms_item
          in models.RunInfoModel.QueryAll()]


def GetByCommitSha(commit_sha):
  return [terms_item.msg for terms_item
          in models.RunInfoModel.QueryBySha(commit_sha)]


def GetById(id):
  result = models.RunInfoModel.Get(id)
  return None if result is None else result.msg


RunInfo


class RunInfoHandler(object):
  def Get(self, id=None, commit_sha=None):
    return GetById(id) if id else GetByCommitSha(commit_sha) if commit_sha else GetAll()

  def GetByCommitSha(self, commit_sha):
    return GetByCommitSha(commit_sha)

  def Create(self, msg):
    msg.createdTimestamp = utils.TimestampUtcNow()
    run_info_model = models.RunInfoModel(msg=msg)
    run_info_model.put()
    msg.id = str(run_info_model.key.id())
    return msg

  def Set(self, msg, id):
    id = str(id)
    run_info_model = models.RunInfoModel.Get(id)
    for name in RunInfoUserFields:
      setattr(run_info_model.msg, name, getattr(msg, name))
    run_info_model.put()
    run_info_model.msg.id = id
    return run_info_model.msg

run_info_handler = RunInfoHandler()
