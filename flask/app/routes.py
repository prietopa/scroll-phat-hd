from flask import render_template
from app import app


TITLE = 'Scroll pHAT HD'


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html', title=TITLE)