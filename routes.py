from webapp2_extras.routes import RedirectRoute

routes = [
    RedirectRoute(r'/', handler='base.handlers.HomeHandler', name='home', strict_slash=True),
    RedirectRoute(r'/logout', handler='base.handlers.LogoutHandler', name='logout', strict_slash=True),
    RedirectRoute(r'/users/me', handler='base.handlers.ProfileHandler', name='profile-me', strict_slash=True),
    # Account Settings
#     RedirectRoute(r'/settings', handler='handlers.AccountIndexHandler', name='account-index', strict_slash=True),
#     RedirectRoute(r'/settings/email', handler='handlers.AccountEmailHandler', name='account-email', strict_slash=True),
#     RedirectRoute(r'/settings/password', handler='handlers.AccountPasswordHandler', name='account-password', strict_slash=True),
# 
#     # Password
#     RedirectRoute(r'/password/reset', handler='handlers.PasswordResetHandler', name='password-reset', strict_slash=True),
#     RedirectRoute(r'/password/reset/<token>', handler='handlers.PasswordResetCompleteHandler', name='password-reset-check', strict_slash=True),
    ]