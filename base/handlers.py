# -*- coding: utf-8 -*-
import webapp2
from webapp2 import redirect_to
from webapp2_extras import jinja2
from engineauth import models

import ndb

import forms

def user_required(handler):
    """
         Decorator for checking if there's a user associated with the current session.
         Will also fail if there's no session present.
     """

    def check_login(self, *args, **kwargs):
        if not self.request.user:
            # If handler has no login_url specified invoke a 403 error
            try:
                return redirect_to('home')
            except (AttributeError, KeyError), e:
                abort(403)
        else:
            return handler(self, *args, **kwargs)

    return check_login

class BaseHandler(webapp2.RequestHandler):
    """
        BaseHandler for all requests all other handlers will
        extend this handler

    """
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    @webapp2.cached_property
    def user(self):
        return self.request.user if self.request.user else None

    @webapp2.cached_property
    def session(self):
        return self.request.session if self.request.session else None

    def get_messages(self, key='_messages'):
        try:
            return self.session.data.pop(key)
        except KeyError:
            return None

    def add_message(self, message, level=None, key='_messages'):
        if not self.session.data.get(key):
            self.session.data[key] = []
        self.session.data[key].append({'message': message, 'level': level})

    def render_template(self, template_name, template_values={}):
        # get the messages if any
        messages = self.get_messages()
        if messages:
            template_values.update({'messages': messages})
        
        # add the user info to the template values
        template_values.update(user=self.user, session=self.session, is_user=False if self.user is None else True)

        self.response.write(self.jinja2.render_template(
                            template_name, **template_values))

    def render_string(self, template_string, template_values={}):
        self.response.write(self.jinja2.environment.from_string(
            template_string).render(**template_values))

    def json_response(self, json):
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(json)


class HomeHandler(BaseHandler):
    def get(self):
        if self.user:
            return self.redirect_to('profile-me')

        if not self.request.app.debug and self.request.scheme != 'https':
            # allow only secure connections in home since the login
            # from home is allowed (ssl doesn't work in dev environment)
            return self.redirect(self.uri_for('home', _scheme='https'))
        
        self.render_template('home.html')

class ProfileHandler(BaseHandler):
    @user_required
    def get(self):
        profiles = None
        emails = None
        user = self.user
        
        if user:
            profiles_done = [p[:p.index(':')] for p in user.auth_ids]
            profile_keys = [ndb.Key('UserProfile', p) for p in user.auth_ids]
            profiles = ndb.get_multi(profile_keys)

            emails = models.UserEmail.get_by_user(user.key.id())
        self.render_template('profile.html', {
                'profiles': profiles,
                'profiles_done': profiles_done,
                'emails': emails,
                'form': self.form,
            })
            
    @user_required
    def post(self):
        if self.form.validate():
            self.user.full_name = self.form.full_name.data
            self.user.put()
            
            email_list = [email.value for email in self.user.get_emails()]
            if self.form.email.data not in email_list:
                self.user.add_email(self.form.email.data)
            
            return self.redirect_to('profile-me')
            
        self.add_message('Please correct the form errors.', 'error')
        return self.redirect_to('profile-me')
        
    @webapp2.cached_property
    def form(self):
        return forms.UserForm(self.request.POST, self.user)

class LogoutHandler(BaseHandler):
    @user_required
    def get(self):
        self.response.delete_cookie('_eauth')
        return self.redirect_to('home')

class EmailValidation(BaseHandler):
    def get(self):
        self.render_template('email-validation.html');