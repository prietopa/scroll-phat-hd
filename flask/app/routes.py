from flask import render_template
from app import app

import time
import math

import scrollphathd
from scrollphathd.fonts import font5x5
from scrollphathd.fonts import font5x7
from six import unichr

from threading import Thread

scrollphathd.clear()
scrollphathd.show()

scrollphathd.rotate(degrees=180)
BRIGHTNESS = 0.3
scrollphathd.set_brightness(BRIGHTNESS)
scrollphathd.set_font(font5x7)
scrollphathd.write_string('Flask up')


class Plasma():

    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def is_active(self):
        return self._running

    def run(self):
        self._running = True
        i = 0

        while self.is_active():
            i += 2
            s = math.sin(i / 50.0) * 2.0 + 6.0

            for x in range(0, 17):
                for y in range(0, 7):
                    v = 0.3 + (0.3 * math.sin((x * s) + i / 4.0)
                               * math.cos((y * s) + i / 4.0))

                    scrollphathd.set_pixel(x, y, v)

            time.sleep(0.01)
            scrollphathd.show()
        else:
            print('Salimos del plasma y limpiamos la pantalla')
            scrollphathd.clear()
            scrollphathd.show()


class Utf8():

    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def is_active(self):
        return self._running

    def run(self):
        self._running = True
        text = [unichr(x) for x in range(256)]
        text = u"{}        ".format(u"".join(text))
        scrollphathd.write_string(text, x=0, y=0, font=font5x7, brightness=BRIGHTNESS)

        while self.is_active():
            scrollphathd.show()
            scrollphathd.scroll()
            time.sleep(0.05)


class Message():

    def __init__(self, text):
        self.text = text
        self._running = True

    def terminate(self):
        self._running = False

    def is_active(self):
        return self._running

    def run(self):
        self._running = True
        
        scrollphathd.write_string(self.text, x=0, y=0, font=font5x7, brightness=BRIGHTNESS)
        while self.is_active():
            scrollphathd.show()
            scrollphathd.scroll()
            time.sleep(0.05)


plasma = Plasma()
utf8 = Utf8()
message = Message('Flask up!! ')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',)


@app.route('/plasma')
def run_plasma():
    cleanup()
    t = Thread(target=plasma.run)
    t.start()
    return render_template('index.html',)


@app.route('/utf8')
def run_utf8():
    cleanup()
    t = Thread(target=utf8.run)
    t.start()
    return render_template('index.html',)


@app.route('/message')
def run_message():
    cleanup()
    t = Thread(target=message.run)
    t.start()
    return render_template('index.html',)


def cleanup():
    if utf8.is_active():
        utf8.terminate()
    if plasma.is_active():
        plasma.terminate()
    if message.is_active():
        message.terminate()

    scrollphathd.set_brightness(BRIGHTNESS)
    scrollphathd.set_font(font5x7)

    scrollphathd.clear()
    scrollphathd.show()

@app.route('/clear')
def clear():
    cleanup()
    return render_template('index.html',)
