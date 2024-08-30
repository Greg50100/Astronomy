import numpy as np
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, get_sun
from astropy.coordinates import solar_system_ephemeris, get_body
import astropy.units as u
from astroplan import Observer, moon_rise_time, moon_set_time, moon_transit_time
from datetime import datetime

# Définir la localisation de Cherbourg
cherbourg = EarthLocation(lat=49.6386*u.deg, lon=-1.6164*u.deg, height=0*u.m)
observer = Observer(location=cherbourg, timezone='UTC')

# Définir la date et l'heure actuelle
now = Time(datetime.utcnow())

# Utiliser les éphémérides JPL pour des positions plus précises
with solar_system_ephemeris.set('de432s'):
    # Calculer les heures de lever, de culmination et de coucher de la lune
    moon_rise = observer.moon_rise_time(now, which='next')
    moon_set = observer.moon_set_time(now, which='next')
    moon_culmination = observer.meridian_transit_time(now, get_body('moon', now), which='next')

print(f"Lever de la lune : {moon_rise.iso}")
print(f"Culmination de la lune : {moon_culmination.iso}")
print(f"Coucher de la lune : {moon_set.iso}")
