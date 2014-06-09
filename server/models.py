# -*- coding: utf-8 -*-

"""Datastore NDB models for metrics per test run.

Our datastore models are specified in python by subclassing "ndb.Model".  We'll
define the message model thats transferred between the client and server as our
canonical model and then define the datastore model in terms of it.
"""

from protorpc import messages

import google.appengine.ext.ndb.msgprop
ndb = google.appengine.ext.ndb


package = "com.appspot.ng-dash"


class Data(messages.Message):
  name = messages.StringField(1)
  description = messages.StringField(2)
  dimensionsJson = messages.StringField(3)
  metricsJson = messages.StringField(4)
  children = messages.MessageField('Data', 5, repeated=True)


class RunInfo(messages.Message):
  id = messages.StringField(1)
  commitSha = messages.StringField(2, required=True)
  createdTimestamp = messages.IntegerField(
      3, variant=messages.Variant.INT32)
  name = messages.StringField(4)
  description = messages.StringField(5)
  # TODO(chirayu): resolve creatorIdentity from the OAUTH identity of the
  # poster.
  creatorIdentity = messages.StringField(6)
  data = messages.MessageField(Data, 7)


class RunInfoModel(ndb.Model):
  msg = ndb.msgprop.MessageProperty(
      RunInfo,
      indexed_fields=[
          "id",
          "commitSha",
          "name",
          ]
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
    return cls._fixup_ids(cls.query(cls.msg.commitSha == sha).fetch(limit))


# For listing all all RunInfo's per commit SHA.
class RunInfoCollection(messages.Message):
  items = messages.MessageField(RunInfo, 1, repeated=True)
