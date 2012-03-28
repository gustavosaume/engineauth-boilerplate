import logging

import webapp2
from webapp2_extras import jinja2

def handle_404(request, response, exception):
    logging.exception(exception)
    
    renderer = jinja2.get_jinja2()
    response.write(renderer.render_template('errors/404.html'))
    
    response.set_status(404)

def handle_500(request, response, exception):
    logging.exception(exception)
    
    renderer = jinja2.get_jinja2()
    response.write(renderer.render_template('errors/500.html'))
    
    response.set_status(500)