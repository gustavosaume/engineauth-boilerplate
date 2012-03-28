from jinja2.filters import do_pprint

config = {}

config['webapp2_extras.sessions'] = {'secret_key': 'wIDjEesObzp5nonpRHDzSp40aba7STuqC6ZRY'}
config['webapp2_extras.auth'] = {
                                #        'user_model': 'models.User',
                                'user_attributes': ['displayName', 'email'],
                                }
config['webapp2_extras.jinja2'] = {'filters': {'do_pprint': do_pprint}}