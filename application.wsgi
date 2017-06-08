#!/usr/bin/env python3

import sys
from iot_api import app as application

sys.path.insert(0, '/var/www/heig-iot')

activate_this = '/var/www/heig-iot/_env/bin/activate.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this)
