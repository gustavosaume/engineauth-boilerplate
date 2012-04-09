from webapp2_extras.routes import RedirectRoute

routes = [
    RedirectRoute(r'/', handler='base.handlers.HomeHandler', name='home', strict_slash=True),
    RedirectRoute(r'/logout', handler='base.handlers.LogoutHandler', name='logout', strict_slash=True),
    RedirectRoute(r'/users/me', handler='base.handlers.ProfileHandler', name='profile-me', strict_slash=True),
    RedirectRoute(r'/password-reset', handler='base.handlers.PasswordResetHandler', name='password-reset'),
    RedirectRoute(r'/new-password', handler='base.handlers.NewPasswordHandler', name='new-password')
    ]