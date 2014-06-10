# -*- coding: utf-8 -*-
"""RESTful API backend for the glossaryapp AngularJS codelab.

Exposes two RESTful services for Terms and Comments.

GET  /api/terms               - Fetch all terms
POST /api/terms               - Create a new term
GET /api/terms/<ID>           - Get a specific term
GET /api/terms/<ID>/comments  - Fetch all comments for the term
POST /api/terms/<ID>/comments - Add a new comments for the term

Exports a WSGI application to serve the Google Cloud Endpoints API for Terms and
Comments.  It uses the same underlying implementation used by the RESTful API -
terms.py:term_handler and comments.py:comment_handler and is an alternate HTTP
API.

  TermApi: An Endpoint handler for manipulating Term models in the backend
  CommentApi: An Endpoint handler for manipulating Term models in the backend
  wsgi_app: A WSGI application contain both the terms and comments APIs.
"""

from protorpc import protojson
import webapp2


class Error(Exception):
  pass


def RestProtoJsonRoute(template, handler, request_type, methods=None, **kwargs):
  """An adapter to produce a webapp2.Route for a RESTful API.

  This adapter simplifies generating RESTful APIs.

  - It automatically determines the REST API methods to be exposed based on the
    methods available on the handler object.
  - It automatically decodes the incoming JSON into the requested protobuf
    object and passes the protobuf object to the handler's method.
  - It automatically serializes the returns protobuf object into JSON that is
    returned to the client.

  Handler objects:
    - Create/POST:
        If the handler object exposes a Create method, the HTTP POST verb is
        exposed on the Route.
    - Delete/DELETE:
        If the handler object exposes a Delete method, the HTTP DELETE verb is
        exposed on the Route.
    - Get/GET:
        If the handler object exposes a Get method, the HTTP GET verb is
        exposed on the Route.
    - Set/PUT:
        If the handler object exposes a Set method, the HTTP PUT verb is
        exposed on the Route.

    The handler object must expose at least one such method.

  Args:
    template: A webapp2.Route template that is passed as is.
    handler: A handler object as described above.
    request_type: The class of the incoming request protobuf that should be
      automatically deserialized.  This must be a subclass of messages.Message.
    methods: If specified, is an optional list that overrides the HTTP verbs
      exposed on the resulting Route.
    **kwargs: Optional list of keyword arguments that are to be passed as-is to
      the webapp2.Route constructor.

  Returns:
    A webapp2.Route object that exposes HTTP verbs on the specified template
    route and delegates actions to the handler's methods.

  Raises:
    Error: The handler must implement at least one method to be exposed.
  """
  # methods is the same parameter that webapp2.Route accepts.
  _methods = []
  if not methods:
    methods = _methods

  # We will add the REST HTTP verbs based on the methods implemented by the
  # provided handler.
  if hasattr(handler, "Create"):
    _methods.append("POST")
  if hasattr(handler, "Delete"):
    raise NotImplementedError(
        "rest_handler.RestProtoJsonRoute: DELETE not implemented.")
  if hasattr(handler, "Get"):
    _methods.append("GET")
  if hasattr(handler, "Set"):
    _methods.append("PUT")

  # A RESTful service must support at least one verb.
  if not methods:
    raise Error("You must have at least one method on the handler.")


  def DecodeProto(data):
    return protojson.decode_message(request_type, data)

  def EncodeProto(msg):
    if msg is None:
      return ""
    elif isinstance(msg, list):
      # A list of ProtoRPC messages needs to be serialized into a JSON list by
      # serializing each individual message.
      msg_list = msg
      csv = ", ".join(protojson.encode_message(msg) for msg in msg_list)
      return "[" + csv + "]"
    else:
      return protojson.encode_message(msg)

  class _RestJsonHandlerAdapter(webapp2.RequestHandler):
    """webapp2 RequestHandler that proxies HTTP method invocations.

    Proxies HTTP methods to to the right method on the RESTful handler.  It
    handles serializing/deserializing the ProtoRPC messages in the request and
    response.
    """

    def get(self, **params):
      # Get requests have no HTTP message body to be parsed.
      result = handler.Get(**params)
      self.response.write(EncodeProto(result))

    def put(self, **params):
      data = DecodeProto(self.request.body) if self.request.body else None
      result = handler.Set(data, **params)
      self.response.write(EncodeProto(result))

    def post(self, **params):
      data = DecodeProto(self.request.body) if self.request.body else None
      result = handler.Create(data, **params)
      self.response.write(EncodeProto(result))

  return webapp2.Route(template,
                       handler=_RestJsonHandlerAdapter,
                       methods=methods,
                       **kwargs)
