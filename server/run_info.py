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


def GetBySha(commitSha):
  return [terms_item.msg for terms_item
          in models.RunInfoModel.QueryBySha(commitSha)]


def GetById(id):
  result = models.RunInfoModel.Get(id)
  return None if result is None else result.msg


class RunInfoHandler(object):
  def Get(self, id=None):
    return GetById(id) if id else GetAll()

  def GetBySha(self, sha):
    return GetBySha(sha)

  def _create_test_data_objects(self, msg)
    model = TestDataModel()
    model.name = msg.name
    model.description = msg.description
    model.dimensions_json = msg.dimensions_json
    model.metrics_json = msg.metrics_json
    model. # ckck

  def Create(self, msg):
    run_info_model = RunInfoModel._model_from_message()
    # Put all the children into the datastore first
    child = self._create_test_data_objects(msg.test_data)
    for child in  # ckck
    msg.createdTimestamp = utils.TimestampUtcNow()
    run_info_model = models.RunInfoModel(msg=msg)
    run_info_model.put()
    msg.id = str(run_info_model.key.id())
    return msg

  def Set(self, msg, id):
    id = str(id)
    run_info_model = models.RunInfoModel.Get(id)

    for name in msg._Message__by_name:
      if name != "id":
        run_info_model.msg[name] = msg[name]
    run_info_model.put()
    run_info_model.msg.id = id
    return run_info_model.msg

run_info_handler = RunInfoHandler()
