# -*- coding: utf-8 -*-
import webapp2
from webapp2 import redirect_to
from webapp2_extras import jinja2, security
from engineauth import models

import time
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

class PasswordResetHandler(BaseHandler):
    def get(self):
        self.render_template('auth/password_reset.html')
    def post(self):
        email = self.request.get('email')
        if not email:
            # validate email address
            # TODO: use WTForm
            self.add_message('Please provide an email address', 'error')
            return self.redirect_to('password-reset')
        
        # validate existence of email address
        auth_id = models.User.generate_auth_id('email', email)
        user = models.User._find_user(auth_id, [email])
        
        if not user:
            self.add_message('No one with that email address was found', 'error')
            return self.redirect_to('password-reset')
            
        profiles = ndb.get_multi(ndb.Key(models.UserProfile, key) for key in user.auth_ids)
        
        if not profiles:
            self.add_message('No one with that email address was found', 'error')
            return self.redirect_to('password-reset')
        
        pwd = None
        for profile in profiles:
            if profile.password:
                pwd = profile.password
        
        if pwd:
            # generate and save reset_token
            timestamp = str(time.time())
            token_value = security.generate_password_hash(pwd+timestamp, length=12)
    
            callback_uri = "%(uri)s?ts=%(ts)s&token=%(token)s&email=%(email)s" %dict(uri=webapp2.uri_for('new-password', _full=True),
                                                                                     ts=timestamp, email=email, token=token_value)
            
            # send validation email
            from google.appengine.api import mail
            
            mail.send_mail(sender="Example.com Support <support@example.com>",
                          to=email,
                          subject="Password reset",
                          body="""
            Dear %(email)s:
            
            Click on the following link to reset your password %(callback)s
            
            Please let us know if you have any questions.
            
            The example.com Team
            """%dict(email=email, callback=callback_uri))
            self.add_message('We sent you an email with instructions to reset your password')
        else:
            self.add_message('You previously associated %(providers)s' %dict(providers=', '.join([profile.key.id() for profile in profiles])))
        return self.redirect_to('password-reset')
        
class NewPasswordHandler(BaseHandler):
    def get(self):
        timestamp = self.request.get('ts')
        email = self.request.get('email')
        token = self.request.get('token')
        
        # validate url token
        auth_id = models.User.generate_auth_id('email', email)
        profile = models.UserProfile.get_by_auth_id(auth_id)
        
        if not security.check_password_hash(profile.password+timestamp, token):
            self.add_message('The information that you\'ve provided '
                            'doesn\'t match our records. '
                            'Please try again.')
            return self.redirect_to('password-reset')
        
        # show update password form
        return self.render_template('auth/password_reset_complete.html', {'form':self.form})

    def post(self):
        # update password
        pass
    
    @webapp2.cached_property
    def form(self):
        return forms.NewPasswordForm(self.request.POST)