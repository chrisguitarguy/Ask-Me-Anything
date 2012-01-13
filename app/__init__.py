import os.path

from flask import Flask, session, g
import redis
from werkzeug.security import gen_salt

templatedir = os.path.join(os.path.dirname(__file__), 'templates')

application = Flask(__name__, template_folder=templatedir)
application.config.from_pyfile('config.py')

@application.before_request
def connect_redis():
    if 'csrf' not in session:
        session['csrf'] = '{}:0'.format(gen_salt(12))
    else:
        csrf = session.get('csrf')
        try:
            token, uses = csrf.split(':', 1)
        except:
            session.pop('csrf')
        else:
            if int(uses) >= 10:
                session['csrf'] = '{}:0'.format(gen_salt(12))
    g.redis = redis.Redis()

import app.views
