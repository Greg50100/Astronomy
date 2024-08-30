from astroplan import Observer, FixedTarget
from astroplan import moon_illumination, moon_phase_angle
from astroplan import download_IERS_A
from astropy.time import Time
from astropy.coordinates import EarthLocation, get_moon
import astropy.units as u

# Télécharger les données IERS nécessaires
download_IERS_A()

# Définir l'emplacement de Cherbourg, France
cherbourg = EarthLocation(lat=49.6386*u.deg, lon=-1.6164*u.deg, height=0*u.m)
observer = Observer(location=cherbourg, timezone='Europe/Paris')

# Définir la date d'observation
date = Time('2024-08-28 00:00:00')

# Obtenir les heures de lever, de coucher et de culmination de la Lune
moon = get_moon(date, location=cherbourg)
moon_rise = observer.moon_rise_time(date, which='next')
moon_set = observer.moon_set_time(date, which='next')
moon_transit = observer.moon_transit_time(date, which='next')

print(f"Heure de lever de la Lune : {moon_rise.iso}")
print(f"Heure de coucher de la Lune : {moon_set.iso}")
print(f"Heure de culmination de la Lune : {moon_transit.iso}")
