from .scrapper import ApiHandler

api = ApiHandler()
api.run()
wsgi_service = api.wsgi