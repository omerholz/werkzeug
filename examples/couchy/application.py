from couchdb.client import Server

from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.wrappers import Request
from werkzeug.wsgi import ClosingIterator

from . import views
from .models import URL
from .utils import STATIC_PATH, local, local_manager, url_map


class Couchy:
    def __init__(self, db_uri):
        local.application = self

        server = Server(db_uri)
        try:
            db = server.create("urls")
        except Exception:
            db = server["urls"]
        self.dispatch = SharedDataMiddleware(self.dispatch,
                                             {"/static": STATIC_PATH})

        URL.db = db

    def dispatch(self, environ, start_response):
        local.application = self
        request = Request(environ)
        local.url_adapter = adapter = url_map.bind_to_environ(environ)
        try:
            endpoint, values = adapter.match()
            handler = getattr(views, endpoint)
            response = handler(request, **values)
        except NotFound:
            response = views.not_found(request)
            response.status_code = 404
        except HTTPException as e:
            response = e
        return ClosingIterator(response(environ, start_response),
                               [local_manager.cleanup])

    def __call__(self, environ, start_response):
        return self.dispatch(environ, start_response)
