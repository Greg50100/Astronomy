#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Aug 2024
@ author: David ALBERTO (www.astrolabe-science.fr)

This script draws the heliocentric positions of Earth and the planets (Mercury, Venus, Mars)
for a given date.
"""
# calling libraries :
import matplotlib.pyplot as plt
from matplotlib import patches
# import datetime as dt
from datetime import datetime, timedelta
import numpy as np
from skyfield.api import load, utc
from skyfield.framelib import ecliptic_frame
import locale
import matplotlib.font_manager as fm
font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
if font_paths:
    plt.rcParams["font.family"] = fm.FontProperties(fname=font_paths[0]).get_name()
else:
    plt.rcParams["font.family"] = "DejaVu Sans"
# locale.setlocale(locale.LC_ALL,'en_US.UTF-8')  # language for month name
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')  # language for month name

# Customized settings : ----------------------------
plt.rcParams["font.family"] = "Arial" # or other local font
plt.rcParams["font.size"] = 8
plt.rcParams['scatter.edgecolors'] = '#464039'
background_color = '#282624' #Fluent Orange Theme (card-background-color: "rgb(40,38,36)" / https://github.com/Madelena/Metrology-for-Hass/blob/main/themes/metro.yaml)
planet_colors = {'mercury': 'gray', 'venus': 'tan', 'earth': 'royalblue', 'mars': 'orangered', 'jupiter barycenter':'orange', 'saturn barycenter':'goldenrod', 'uranus barycenter' : 'skyblue', 'neptune barycenter' : 'mediumblue'}
planet_names = ['mercury', 'venus', 'mars', 'jupiter barycenter', 'saturn barycenter', 'uranus barycenter', 'neptune barycenter']  # named reckoned by the Skyfield library
delay = 0 # number of days after 2024/1/1
date = datetime.now() + timedelta(days=delay)
# ---------------------------------------------------

ts = load.timescale()
"""
The ephemerides file has to be downloaded once, then loaded from its local folder.
"""
eph = load('de421.bsp')  # loaded from the folder
#eph = load('../skyfield-ephemerides/de421.bsp')  # download
sun, earth = eph['sun'], eph['earth']
planets = {name: eph[name] for name in planet_names}
# ---------------------------------------------------
#  ------------------- FUNCTIONS --------------------

def helio_coordinates(planet, t):
    """
    planet : Skyfield celestial body
    date : date ou série de dates Skyfield
    returns heliocentric longitude in radians, and distance from the Sun (au)
    """
    lat, lon, distance = sun.at(t).observe(planet).frame_latlon(ecliptic_frame)
    lon = lon.radians
    distance = distance.au
    return lon, distance

#  end of functions--------------

#  Setting figure and axes :

for name, planet in planets.items():
    fig = plt.figure()
    fig.patch.set_facecolor(background_color)

    date = date.replace(tzinfo=utc) # declaring timezone info before conversion
    t = ts.from_datetime(date) # conversion to a Skyfield date

    ax2 = plt.subplot(122, projection='polar')  # right plot
    ax2.set(
            xticks = ([]),
            yticks = ([]),
            facecolor = background_color,
            )
    ax2.spines['polar'].set_color('#464039')  # Set the color of the outer circle

    x_earth, y_earth = helio_coordinates(earth, t)
    x_planet, y_planet = helio_coordinates(planet, t)

    #  plotting the sun & planets
    ax2.plot([0,x_earth],[0, y_earth], c='#464039', lw=0.7)
    ax2.plot([0,x_planet],[0, y_planet], c='#464039', lw=0.7)
    ax2.plot([x_planet,x_earth],[y_planet, y_earth], c='#464039', lw=0.7)

    ax2.scatter(0, 0, c='gold', s=100, zorder=2)
    ax2.scatter(x_earth, y_earth, label='Terre', c='royalblue', zorder=2)
    ax2.scatter(x_planet, y_planet, label=name.capitalize(), c=planet_colors[name], zorder=2)

    plt.legend(loc=1, facecolor='#908c88', edgecolor='#1b1a18', labelcolor='#1b1a18')

    fig.savefig('/data/astronomy/images/' + f'{name}_position.png', dpi=300, bbox_inches='tight', pad_inches=0.05)

