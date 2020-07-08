from flask import Flask
from flask_babel import Babel
from flask import request

app = Flask(__name__)

from app import routes
babel = Babel(app)

import scrollphathd
from scrollphathd.api.http import scrollphathd_blueprint
from scrollphathd.fonts import font3x5

# Set the font
scrollphathd.set_font(font3x5)
# Set the brightness
scrollphathd.set_brightness(0.2)
#  Pimoroni Scroll Bot)
scrollphathd.rotate(degrees=180)

app.register_blueprint(scrollphathd_blueprint)


@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(app.Config['LANGUAGES'])
    return 'es'
    # return 'en'
