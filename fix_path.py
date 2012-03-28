import os
import sys

# add the external libs
if not os.path.join(os.path.dirname(__file__), 'plugins') in sys.path:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'plugins', 'auth'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'plugins', 'auth', 'lib'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'plugins'))