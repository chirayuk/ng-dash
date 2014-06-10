# -*- coding: utf-8 -*-

from protorpc import messages
from protorpc.messages import (
    IntegerField, StringField, MessageField, Variant)

import google.appengine.ext.ndb.msgprop
from google.appengine.ext.ndb import (
    DateTimeProperty, StringProperty, StructuredProperty, KeyProperty
ndb = google.appengine.ext.ndb


package = "com.appspot.ng-dash"



class TestData(messages.Message):
  name = StringField(1)
  description = StringField(2)
  dimensions_json = StringField(3)
  metrics_json = StringField(4)
  parent_id = StringField(5)
  children = MessageField('TestData', 6, repeated=True)
  dimensions_merged_json = StringField(7)
  dimensions_flattened_json = StringField(8)


class NvModel(ndb.Model):
  name = ndb.StringProperty()
  value = ndb.StringProperty()


class TestDataModel(ndb.Model):
  name = StringProperty()
  description = StringProperty()
  dimensions_json = StringProperty()
  metrics_json = StringProperty();
  parent = KeyProperty(kind='TestDataModel')
  children = KeyProperty(kind='TestDataModel', repeated=true)
  # For searching
  dimensions = StructuredProperty(NvModel, repeated=True)
  dimensions_merged = StructuredProperty(NvModel, repeated=True)
  dimensions_flattened = StructuredProperty(NvModel, repeated=True)
  metrics = StructuredProperty(NvModel, repeated=True)


class RunInfo(messages.Message):
  id = StringField(1)
  commit_sha = StringField(2, required=True)
  tree_sha = StringField(3, required=True)
  creation_timestamp = messages.IntegerField(4, variant=Variant.INT32)
  name = StringField(5)
  description = StringField(6)
  creator_email = StringField(7)
  test_data = MessageField(TestData, 8)


class RunInfoModel(ndb.Model):
  id = StringProperty()
  commit_sha = StringProperty()
  tree_sha = StringProperty()
  creation_time = DateTimeProperty(auto_now_add=True)
  name = StringProperty()
  description = StringProperty()
  # stable user.user_id()
  creator_id = StringProperty()
  creator_email = StringProperty()
  test_data = KeyProperty(kind=TestDataModel)


  @classmethod
  def Get(cls, id):
    result = ndb.Key(cls, int(id)).get()
    return result

  @classmethod
  def _message_from_model(cls, model):
    msg = RunInfo()
    msg.id = str(model.key.id())
    msg.commit_sha = model.commit_sha
    msg.tree_sha = model.tree_sha
    msg.creation_timestamp = int(calendar.timegm(model.creation_time.utctimetuple()))
    msg.name = model.name
    msg.description = model.description
    msg.creator_email = model.creator_email
    msg.test_data = model.test_data._message_from_model()

  @classmethod
  def _model_from_message(cls, msg):
    model = RunInfoModel()
    # The following fields will NOT be copied:
    # id, creation_time, creator_id, creator_email
    # test_data
    model.commit_sha = msg.commit_sha
    model.tree_sha = msg.tree_sha
    model.name = msg.name
    model.description = msg.description
    return model


  @classmethod
  def QueryAll(cls, limit=20):
    return cls.query().fetch(limit)

  @classmethod
  def QueryBySha(cls, sha, limit=20):
    return cls.query(cls.msg.commit_sha == sha).fetch(limit)


# For listing all all RunInfo's per commit SHA.
class RunInfoCollection(messages.Message):
  items = MessageField(RunInfo, 1, repeated=True)
