#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Aug 2024
@ author: David ALBERTO (www.astrolabe-science.fr)

This script draws the aspect of the planetary discs (phases) for a given date,
and the heliocentric positions of Earth, Venus, Mercury, and Mars.
Displays percent of disc illuminated and phase angle of each planet.
The phase angle is the angle which vertex is the observed planet,
 not the earth.
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
plt.rcParams['scatter.edgecolors'] = 'black'
planet_colors = {'mercury': 'gray', 'venus': 'tan', 'earth': 'royalblue', 'mars': 'orangered', 'jupiter barycenter':'orange', 'saturn barycenter':'goldenrod', 'uranus barycenter' : 'skyblue', 'neptune barycenter' : 'mediumblue'}
background_color = '#282624' #Fluent Orange Theme (card-background-color: "rgb(40,38,36)" / https://github.com/Madelena/Metrology-for-Hass/blob/main/themes/metro.yaml)
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

def phase_angle(t, planet):
    """
    Parameters
    ----------
    t : TYPE        : Skyfield date
    planet : Skyfield celestial body
    Returns the phase angle in degrees and percent illuminated
    -------
    """
    sun_position = planet.at(t).observe(sun)
    earth_position = planet.at(t).observe(earth)
    phase_angle_deg = sun_position.separation_from(earth_position).degrees
    phase_angle_rad = (np.radians(phase_angle_deg))
    f = 50 * (1 + np.cos(phase_angle_rad))  # percent illuminated
    return phase_angle_deg, f

def lightside(planet):
    """
    calculates geocentric longitudes of the Sun and the planet, and
    finds from which side the planet is illuminated :
        returns True if sunlight comes from the left, False otherwise.
    """
    lat, lon_sun, distance = earth.at(t).observe(sun).frame_latlon(ecliptic_frame)
    lat, lon_planet, distance = earth.at(t).observe(planet).frame_latlon(ecliptic_frame)
    long_diff = (lon_sun.degrees - lon_planet.degrees)  # difference in geocentric longitude
    if long_diff > 180:
        long_diff = long_diff - 360
    elif long_diff < -180:
        long_diff = long_diff + 360
    if long_diff < 0:
        left = False
    else:
        left = True
    return left

def radius(t, planet):
    """
    calculates the planet's radius as seen from Earth,
    from its distance.
    Returns normalized radius (float).
    """
    lat, lon, distance = earth.at(t).observe(planet).frame_latlon(ecliptic_frame)
    distance = distance.au
    radius = 0.25/distance
    return radius
    
# --------------------------------------
def disk(p, phase, axe, planet, color):
    """
    Parameters
    ----------
    p : TYPE float
        DESCRIPTION : percent illuminated (0-100)
    phase : phase angle (0 - 180°)
    ax : ax 
    Draws the aspect of the planetary disc
    """
    R = radius(t, planet)
    b = R * (np.cos(np.radians(phase))) # half small axis of the terminator's ellipse
    limb = patches.Circle((0,0),R,facecolor=color,edgecolor='k',zorder=0,
                           linewidth=0.5)
    axe.add_patch(limb)  # edge of the disc, for a white background
    if lightside(planet):
        black_half = patches.Wedge((0,0), R, -90, 90, color='k',ec='None')
    else:
        black_half = patches.Wedge((0,0), R, 90, 270, color='k',ec='None')
    axe.add_patch(black_half)

    if phase >= 0 and phase < 90:
        ellipse_color = color
    else:
        ellipse_color = 'black'
    ellipse = patches.Ellipse((0,0), 2 * b, 2 * R,color = ellipse_color,lw=0)
    axe.add_patch(ellipse)

    # display data :
    axe.text(0.98,0.98,f'{round(p,2)} %',ha='right',va='top',fontsize=10,
             c = 'white',
             transform=axe.transAxes)
    axe.text(0.02,0.98,f'phase angle: {round(phase,1)}°',ha='left',va='top',fontsize=10,
             c = 'white',
             transform=axe.transAxes)
    axe.text(0.5,0.02,date.strftime('%d %b %Y'),ha='center',va='bottom',fontsize=10,
             c = 'white', transform=axe.transAxes)

#  end of functions--------------

#  Setting figure and axes :

for planet_name in planet_names:
    fig, ax = plt.subplots(figsize=(5, 5))  # one axe for each planet
    ax.set(
        aspect = 'equal',
        xlim = (-1,1),
        ylim = (-1,1),
        xticks = ([]),
        yticks = ([]),
        facecolor = background_color,
    )
    
    date = date.replace(tzinfo=utc) # declaring timezone info before conversion
    t = ts.from_datetime(date) # conversion to a Skyfield date
    planet = planets[planet_name]
    phase, f = phase_angle(t, planet)
    disk(f, phase, ax, planet, planet_colors[planet_name])

    fig.savefig('/data/astronomy/images/' + f'{planet_name}_phase.png', dpi=300, bbox_inches='tight', pad_inches=0)

