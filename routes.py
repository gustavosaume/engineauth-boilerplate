from webapp2_extras.routes import RedirectRoute

routes = [
    RedirectRoute(r'/', handler='base.handlers.HomeHandler', name='home', strict_slash=True),
    RedirectRoute(r'/logout', handler='base.handlers.LogoutHandler', name='logout', strict_slash=True),
    RedirectRoute(r'/users/me', handler='base.handlers.ProfileHandler', name='profile-me', strict_slash=True),
    RedirectRoute(r'/email-validation', handler='base.handlers.EmailValidation', name='email-validation', strict_slash=True),
    ]