import numpy as np
from astropy.time import Time
from astropy.coordinates import EarthLocation, get_body
from astropy.coordinates import AltAz
import astropy.units as u
from datetime import datetime, timedelta

# Définir la localisation de Cherbourg
cherbourg = EarthLocation(lat=49.6386*u.deg, lon=-1.6164*u.deg, height=0*u.m)

# Définir la date et l'heure actuelle
now = datetime.utcnow()
time = Time(now)

# Définir la plage de temps pour la recherche (24 heures)
delta_hours = 24
times = time + (delta_hours * u.hour * (np.linspace(0, 1, 100)))

# Obtenir les altitudes de la lune
altaz_frame = AltAz(obstime=times, location=cherbourg)
moon_altaz = get_body("moon", times, location=cherbourg).transform_to(altaz_frame)

# Trouver les moments de lever, culmination et coucher de la lune
moon_rise = times[np.where(np.diff(np.sign(moon_altaz.alt.deg)) > 0)[0]]
moon_set = times[np.where(np.diff(np.sign(moon_altaz.alt.deg)) < 0)[0]]
moon_culmination = times[np.argmax(moon_altaz.alt.deg)]

print(f"Lever de la lune : {moon_rise.iso}")
print(f"Culmination de la lune : {moon_culmination.iso}")
print(f"Coucher de la lune : {moon_set.iso}")
