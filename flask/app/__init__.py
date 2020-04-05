from flask import Flask
from flask_babel import Babel
from flask import request

app = Flask(__name__)

from app import routes
babel = Babel(app)


@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(app.Config['LANGUAGES'])
    return 'es'
    # return 'en'
