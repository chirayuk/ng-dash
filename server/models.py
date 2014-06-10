# -*- coding: utf-8 -*-

"""Datastore NDB models for metrics per test run.

Our datastore models are specified in python by subclassing "ndb.Model".  We'll
define the message model thats transferred between the client and server as our
canonical model and then define the datastore model in terms of it.
"""

from protorpc import messages
from protorpc.messages import (
    IntegerField,
    MessageField,
    StringField,
    Message,
    Variant,
)

import google.appengine.ext.ndb.msgprop
from google.appengine.ext.ndb import (
    Model,
)

ndb = google.appengine.ext.ndb
MessageProperty = ndb.msgprop.MessageProperty


package = "com.appspot.ng-dash"


class Data(Message):
  name = StringField(1)
  description = StringField(2)
  dimensions_json = StringField(3)
  metrics_json = StringField(4)
  children = MessageField('Data', 5, repeated=True)


class RunInfo(Message):
  id = StringField(1)
  creation_timestamp = IntegerField(2, variant=Variant.INT32)
  creator_id = StringField(3)
  commit_sha = StringField(4, required=True)
  tree_sha = StringField(5)
  name = StringField(6)
  description = StringField(7)
  data = MessageField(Data, 8)


RunInfoFields = frozenset(RunInfo._Message__by_name)
RunInfoSystemFields = frozenset(("id", "creation_timestamp", "creator_id"))
RunInfoUserFields = RunInfoFields.difference(RunInfoSystemFields)


class RunInfoModel(Model):
  msg = MessageProperty(
      RunInfo,
      indexed_fields=["id", "commit_sha", "tree_sha", "name"]
      )

  @classmethod
  def Get(cls, id):
    result = ndb.Key(cls, int(id)).get()
    result.msg.id = str(result.key.id())
    return result

  @classmethod
  def _fixup_ids(self, results):
    for result in results:
      result.msg.id = str(result.key.id())
    return results

  @classmethod
  def QueryAll(cls, limit=20):
    return cls._fixup_ids(cls.query().fetch(limit))

  @classmethod
  def QueryBySha(cls, sha, limit=20):
    return cls._fixup_ids(cls.query(cls.msg.commit_sha == sha).fetch(limit))


# For listing all all RunInfo's per commit SHA.
class RunInfoCollection(Message):
  items = MessageField(RunInfo, 1, repeated=True)
