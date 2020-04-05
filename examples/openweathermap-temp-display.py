#!/usr/bin/env python
# openweathermap-temp-display.py
#
# Python script to grab Openweathermap temperature data and display on scrollphathd. #
#
# Tips on how to use API effectively    (https://openweathermap.org/appid#work)
# 1.- We recommend making calls to the API no more than one time every 10 minutes for one location (city / coordinates / zip-code). 
# This is due to the fact that weather data in our system is updated no more than one time every 10 minutes.
# 2.- The server name is api.openweathermap.org. Please, never use the IP address of the server.
# 3.- Better call API by city ID instead of a city name, city coordinates or zip code to get a precise result. The list of cities' IDs is here.
# 4.- Please, mind that Free and Startup accounts have limited service availability. If you do not receive a response from the API, 
# please, wait at least for 10 min and then repeat your request. We also recommend you to store your previous request.
#
# What happens when your account exceeds a limit of calls 
# Response: {
#   "cod": 429,
#   "message": "Your account is temporary blocked due to exceeding of requests limitation of your subscription type. 
#   Please choose the proper subscription http://openweathermap.org/price"
# }

import scrollphathd  # default scrollphathd library
from scrollphathd.fonts import font3x5
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2  # used to make web calls to Openweathermap
import json         # used to parse Openweathermap JSON data
import time         # returns time values
import os

# Pimoroni Scroll Bot
scrollphathd.rotate(degrees=180)

# Openweathermap API key
OWM_API_KEY = 'd4c12ecaa47fc9be14ff1ab81ad462c5'          # (&appid=OWM_API_KEY) make sure to put your unique wunderground key in here
OWM_CITY = 'Mostoles,es'                    # q=OWM_CITY
OWM_CITY_ID = 3116025                       # id=OWM_CITY_ID    http://bulk.openweathermap.org/sample/city.list.json.gz
OWM_LANG = 'es'                             # &lang=OWM_LANG
OWM_UNITS = 'metric'                        # &units=OWM_UNITS

# Display settings
BRIGHT = 0.2
DIM = 0.1
GUST_BRIGHTNESS = 0.2     # show gusts as a bright dot
WIND_BRIGHTNESS = 0.1     # show current speed as a slightly dimmer line

# "Knight Rider" pulse delay. See comments below for description of what this is.
#    Note that this loop uses the lion's share of CPU, so if your goal is to minimize CPU usage, increase the delay.
#    Of course, increasing the delay results in a slightly less cool KR pulse. In practice, a value of 0.05 results in ~16% Python CPU utilization on
#    a Raspberry Pi Zero-W. Increasing this to 0.1 drops CPU to ~10%, of course YMMV.
KR_PULSE_DELAY = 0.05

def get_current_weather_data():
    """ https://openweathermap.org/current """

    # Get current conditions. 
    url_str = 'http://api.openweathermap.org/data/2.5/weather?id={}&lang={}&units={}&appid={}'.format(OWM_CITY_ID, OWM_LANG, OWM_UNITS, OWM_API_KEY)
    try:
        response = urllib2.urlopen(url_str)
    except urllib2.HTTPError as e:
        e.msg = "{} (Did you set the API key?)".format(e.msg)
        raise (e)

    json_string = response.read()                   # load into a json string
    parsed_cond = json.loads(json_string.decode())  # parse the string into a json catalog
    response.close()

    # build current temperature string
    description = parsed_cond['weather']['description']
    temp = float(parsed_cond['main']['temp'])
    pressure = parsed_cond['main']['pressure']
    humidity = parsed_cond['main']['humidity']
    visibility = parsed_cond['visibility']
    wind = float(parsed_cond['wind']['speed'])
    clouds = parsed_cond['clouds']['all']

    return


# draw_kr_pulse(position, direction) - draws a Knight Rider-style pulsing pixel. I put this in so that I could tell that the app was running, since weather
# data sometimes doesn't change very frequently. Plus it's cool. In a geeky sort of way. :-)
#
# position = 1,2,3,4,5 (eg which position on the line you want to illuminate)
# direction = -1,1 (-1 = left, 1 = right). This is used so we know which previous pixel to turn off
def draw_kr_pulse(pos, dir):
    # clear 5 pixel line (easier than keeping track of where the previous illuminated pixel was)
    scrollphathd.clear_rect(12, 5, 5, 1)
    x = pos + 11                       # increase position to the actual x offset we need
    scrollphathd.set_pixel(x, 5, 0.2)  # turn on the current pixel
    scrollphathd.show()
    time.sleep(KR_PULSE_DELAY)

    return


# draw_temp_trend(dir)
# Draws an up arrow, down arrow, or equal sign on the rightmost 3 pixels of the display. Also show wind speed/gusts as a bar on the bottom.
#    dir = 0 (equal), 1 (increasing), -1 (decreasing)
def draw_temp_trend(dir):

    if dir == 0:                                   # equal - don't display anything. Clear the area where direction arrow is shown
        scrollphathd.clear_rect(14, 0, 3, 6)
    elif dir == 1:                                 # increasing = up arrow. Draw an up arrow symbol on the right side of the display
        for y in range(0, 5):
            scrollphathd.set_pixel(15, y, BRIGHT)  # draw middle line of arrow
        scrollphathd.set_pixel(14, 1, BRIGHT)      # draw the 'wings' of the arrow
        scrollphathd.set_pixel(16, 1, BRIGHT)
    elif dir == -1:                                # decreasing = down arrow
        for y in range(0, 5):
            scrollphathd.set_pixel(15, y, BRIGHT)  # draw middle line of arrow
        scrollphathd.set_pixel(14, 3, BRIGHT)
        scrollphathd.set_pixel(16, 3, BRIGHT)

    return


# draw_wind_line() - draws a single line indicator of wind speed and wind gusts on the bottom of the display
# Current wind speed is shown as as bright line and gusts as as dim line.
#
# Calculation: calculate a ratio (17 pixels / max wind speed) and multiply by actual wind speed, rounding
#    to integer, yielding the number of pixels on 'x' axis to illuminate.
def draw_wind_line():
    global wind_speed
    global wind_gusts
    wind_multiplier = (17.0 / MAX_WIND_SPEED)
    if DEBUG:
        print("Wind multiplier: ", wind_multiplier)
    wind_calc = wind_multiplier * wind_speed
    if DEBUG:
        print("wind calc: ", wind_calc)
    wind_calc = int(wind_calc)  # convert to int
    if wind_calc > 17:  # just in case something goes haywire, like a hurricane :-)
        wind_calc = 17
    gust_calc = wind_multiplier * wind_gusts
    if DEBUG:
        print("gust calc: ", gust_calc)
    gust_calc = int(gust_calc)
    if gust_calc > 17:
        gust_calc = 17
    if DEBUG:
        print("Wind speed, calc", wind_speed, wind_calc)
        print("wind gusts, calc", wind_gusts, gust_calc)
    # Draw the wind speed first
    for x in range(0, wind_calc):
        scrollphathd.set_pixel(x, 6, WIND_BRIGHTNESS)
    # Now draw the gust indicator as a single pixel
    if gust_calc:  # only draw if non zero
        scrollphathd.set_pixel(gust_calc - 1, 6, GUST_BRIGHTNESS)
    return


def display_temp_value(description, temp):
    global actual_str
    global feels_like_str
    # clear the old temp reading. If temp > 35 then clear an extra digit's worth of pixels
    if temp < 35:
        scrollphathd.clear_rect(0, 0, 12, 5)
    else:
        scrollphathd.clear_rect(0, 0, 17, 5)

    scrollphathd.write_string(description, x=0, y=0, font=font3x5, brightness=BRIGHT)
    scrollphathd.show()
    time.sleep(1)
    return


# Initial weather data poll and write to display
get_weather_data()
display_temp_value()  # change this to ACTUAL at the top if you want to display actual temp instead of feels like temp
draw_wind_line()

# Loop forever until user hits Ctrl-C

while True:
    if not (int(time.time()) % POLL_INTERVAL):
        prev_temp = current_temp
        get_weather_data()
        scrollphathd.clear()
        draw_wind_line()
        # don't show temp trend arrow if > 100 degrees or < -10 degrees -- not enough room on the display.
        if current_temp < average_temp and (current_temp < 100 or current_temp < -9):
            if DEBUG:
                print(time.asctime(time.localtime(time.time())), "Actual temp", actual_str, "Feels like temp", feels_like_str, "-")
            draw_temp_trend(-1)
        elif current_temp == average_temp and (current_temp < 100 or current_temp < -9):
            if DEBUG:
                print(time.asctime(time.localtime(time.time())), "Actual temp", actual_str, "Feels like temp", feels_like_str, "=")
            draw_temp_trend(0)
        elif current_temp > average_temp and (current_temp < 100 or current_temp < -9):
            if DEBUG:
                print(time.asctime(time.localtime(time.time())), "Actual temp", actual_str, "Feels like temp", feels_like_str, "+")
            draw_temp_trend(1)
        display_temp_value()  # if you want actual temp, just change to ACTUAL

    # Pulse a pixel, Knight Rider style, just to show that everything is alive and working. Sleeps also keep Python from consuming 100% CPU
    # Use line 5, 14-17
    for pulse in range(1, 5):
        draw_kr_pulse(pulse, 1)    # left to right
    for pulse in range(5, 1, -1):
        draw_kr_pulse(pulse, -1)   # back the other way

# termination code; clear the display
scrollphathd.clear()
scrollphathd.show()
print("Exiting....")
