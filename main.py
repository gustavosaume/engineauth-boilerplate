# -*- coding: utf-8 -*-
import fix_path
import os

import webapp2

from routes import routes
from config import config

from errors import error_handlers

DEBUG = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
application = webapp2.WSGIApplication(routes, debug=DEBUG, config=config)

# assign the error handlers
application.error_handlers[404] = error_handlers.handle_404
application.error_handlers[500] = error_handlers.handle_500
