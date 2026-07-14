from werkzeug.wrappers import Response

class PrefixMiddleware:
    """
    WSGI middleware that mounts a Flask (or any WSGI) app under a URL prefix.
    Example: /app -> routes become /app/*
    """

    def __init__(self, app, prefix):
        self.app = app
        self.prefix = "/" + prefix.strip("/")

    @classmethod
    def init_app(cls, app):
        """
        Flask integration helper:
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=...)
        """
        prefix = app.config.get("PREFIX_MIDDLEWARE_PREFIX")
        if prefix:
            app.wsgi_app = cls(app.wsgi_app, prefix=prefix)

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        prefix = self.prefix

        # Match prefix
        if not (path == prefix or path.startswith(prefix + "/")):
            response = Response(
                "URL does not belong to the app.",
                status=404,
                content_type="text/plain",
            )
            return response(environ, start_response)

        # Update WSGI routing variables
        environ["SCRIPT_NAME"] = prefix

        new_path = path[len(prefix):]
        environ["PATH_INFO"] = new_path if new_path else "/"

        return self.app(environ, start_response)
