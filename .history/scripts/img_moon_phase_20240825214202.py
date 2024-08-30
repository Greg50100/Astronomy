#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Aug 2024
@ author: David ALBERTO (www.astrolabe-science.fr)

Ce script trace l'aspect de la Lune vue depuis la Terre, pour une
date donnée, ainsi que les positions géocentriques de la Lune et 
du Soleil à la meme date.
Sont indiqués l'angle de phase de la Lune et le pourcentage
d'éclairement du disque lunaire vu depuis la Terre.
L'angle de phase est l'angle entre la direction de la Terre et celle
du Soleil, depuis la Lune.
"""
# appel des modules :
import os
import matplotlib.pyplot as plt
from matplotlib import patches
from datetime import datetime, timedelta
import pytz
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

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')  # language for month name

# paramètres à personnaliser : ----------------------------
# plt.rcParams["font.family"] = "Arial" # ou autre police installée
plt.rcParams["font.size"] = 8
plt.rcParams['scatter.edgecolors'] = 'black'
couleur_lune = 'lightgray'
background_color = '#282624'
long_fleche = 3.3e5  # longueur de la flèche pointant le Soleil
# ---------------------------------------------------

ts = load.timescale()
"""
Le fichier d'éphémérides doit etre téléchargé une fois, puis chargé
depuis son répertoire.
"""
eph = load('de421.bsp')  # loaded from the folder
#eph = load('../skyfield-ephemerides/de421.bsp')  # download
sun, earth = eph['sun'], eph['earth']
lune = eph['moon']
# ---------------------------------------------------
#  ------------------- FUNCTIONS --------------------

def phase_angle(t):
    """
    Parameters
    ----------
    t : TYPE        : date Skyfield 
    Returns the phase angle in degrees and percent illuminated
    -------
    """
    sun_position = lune.at(t).observe(sun)
    earth_position = lune.at(t).observe(earth)
    phase_angle_deg = sun_position.separation_from(earth_position).degrees
    phase_angle_rad = (np.radians(phase_angle_deg))
    f = 50 * (1 + np.cos(phase_angle_rad))  # percent illuminated
    return phase_angle_deg, f
    
def lightside():
    """
    calculates geocentric longitudes of the Sun and the lune, and
    finds from which side the lune is illuminated :
        returns True if sunlight comes from the left, False otherwise.
    """
    lat, lon_sun, distance = earth.at(t).observe(sun).frame_latlon(ecliptic_frame)
    lat, lon_lune, distance = earth.at(t).observe(lune).frame_latlon(ecliptic_frame)
    long_diff = (lon_sun.degrees - lon_lune.degrees)  # difference in geocentric longitude
    if long_diff > 180:
        long_diff = long_diff - 360
    elif long_diff < -180:
        long_diff = long_diff + 360
    if long_diff < 0:
        left = False
    else:
        left = True
    # printing controls:
    # print(lon_sun.degrees)
    # print(lon_lune.degrees)
    # print(long_diff)
    # print('left ? :', left)
    return left

def radius(t):
    """
    calculates the moon's radius as seen from Earth,
    from its distance.
    Returns normalized radius (float).
    """
    lat, lon, distance = earth.at(t).observe(lune).frame_latlon(ecliptic_frame)
    distance = distance.au
    radius = 0.00201/distance
    return radius
    
# --------------------------------------
def disk(p, phase, axe):
    """
    Parameters
    ----------
    p : TYPE float
        DESCRIPTION : percent illuminated (0-100)
    phase : phase angle (0 - 180°)
    ax : ax 
    Draws the aspect of the luneary disc
    """
    R = radius(t)
    b = R * (np.cos(np.radians(phase))) # half small axis of the terminator's ellipse
    limb = patches.Circle((0,0),R,facecolor=couleur_lune,edgecolor='k',zorder=0,
                           linewidth=1)
    axe.add_patch(limb)  # edge of the disc, for a white background
    if lightside():
        black_half = patches.Wedge((0,0), R, -90, 90, color=background_color ,ec='None')
    else:
        black_half = patches.Wedge((0,0), R, 90, 270, color=background_color ,ec='None')
    axe.add_patch(black_half)

    if phase >= 0 and phase < 90:
        ellipse_color = couleur_lune
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
    axe.text(0.5,0.02,date.strftime('%d %b %Y %H:%M:%S'),ha='center',va='bottom',fontsize=10,
             c = 'white', transform=axe.transAxes)

#  end of functions--------------

#  Setting figure and axes :

for delay in range(1):
    fig, ax = plt.subplots(figsize=(5, 5))  # one axe for each planet
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Adjust margins to reduce white space
    ax.set(
        aspect = 'equal',
        xlim = (-1,1),
        ylim = (-1,1),
        xticks = ([]),
        yticks = ([]),
        facecolor = background_color,
                )
    date = datetime.now(tz=pytz.timezone("Europe/Paris")) + timedelta(days=delay)   
    t = ts.from_datetime(date) # conversion to a Skyfield date
    phase, f = phase_angle(t)
    disk(f, phase, ax)
    
    file_name = 'moon_phase'
    fig.savefig('/data/astronomy/images/' + file_name + '.png', dpi=300, bbox_inches='tight', pad_inches=0)  # Save figure with tight bounding box
    # plt.close()
