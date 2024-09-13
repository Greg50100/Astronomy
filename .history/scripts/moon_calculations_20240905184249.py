from skyfield.api import N, W, load, wgs84
from skyfield import almanac
from datetime import timedelta
import pytz
from math import cos


# Charger les éphémérides et définir l'observateur
ts = load.timescale()
t = ts.now()
dt = t.utc_datetime()
t0 = ts.utc(dt.year, dt.month, dt.day)
t1 = ts.utc((dt + timedelta(days=1)).year, (dt + timedelta(days=1)).month, (dt + timedelta(days=1)).day)
t2 = ts.utc((dt + timedelta(days=2)).year, (dt + timedelta(days=2)).month, (dt + timedelta(days=2)).day)

eph = load('de421.bsp')
earth = eph['earth']
cherbourg = wgs84.latlon(49.6386 * N, 1.6163 * W)  # Exemple de coordonnées pour Cherbourg
cherbourg_observer = earth + cherbourg

# Définir le fuseau horaire de Paris
paris_tz = pytz.timezone('Europe/Paris')

def nearest_minute(dt):
    return (dt + timedelta(seconds=30)).replace(second=0, microsecond=0)

def get_next_moonrise_moonset(observer, t0, t1):
    moon = eph['moon']
    f_moon = almanac.risings_and_settings(eph, moon, observer)
    times_moon, events_moon = almanac.find_discrete(t0, t1, f_moon)

    next_moonrise = None
    next_moonset = None

    for t, e in zip(times_moon, events_moon):
        if t.utc_datetime() > dt:
            rounded_time = nearest_minute(t.utc_datetime())
            rounded_time_paris = rounded_time.astimezone(paris_tz)
            if e and next_moonrise is None:
                next_moonrise = rounded_time_paris
            elif not e and next_moonset is None:
                next_moonset = rounded_time_paris
            if next_moonrise and next_moonset:
                break

    return next_moonrise, next_moonset

def get_moon_altaz(t):
    astrometrics = cherbourg_observer.at(t).observe(eph['moon'])
    apparent = astrometrics.apparent()
    alt, az, d = apparent.altaz()
    return alt, az, d

def get_moon_ra_dec(t):
    astrometrics = cherbourg_observer.at(t).observe(eph['moon'])
    apparent = astrometrics.apparent()
    ra, dec, d = apparent.radec()
    return ra, dec, d

def get_moon_phase_angle(t):
    sun = eph['sun']
    moon = eph['moon']
    astrometrics = cherbourg_observer.at(t).observe(moon)
    apparent_moon = astrometrics.apparent()
    astrometrics = cherbourg_observer.at(t).observe(sun)
    apparent_sun = astrometrics.apparent()
    return apparent_moon.separation_from(apparent_sun).degrees

def get_moon_illumination(t):
    sun = eph['sun']
    moon = eph['moon']

    astrometrics_moon = cherbourg_observer.at(t).observe(moon)
    apparent_moon = astrometrics_moon.apparent()

    astrometrics_sun = cherbourg_observer.at(t).observe(sun)
    apparent_sun = astrometrics_sun.apparent()

    illumination = (cos(apparent_moon.separation_from(apparent_sun).radians))
    return illumination



next_moonrise, next_moonset = get_next_moonrise_moonset(cherbourg, t0, t2)

print(f"Next Moonrise: {next_moonrise.strftime('%Y-%m-%d %H:%M')}")
print(f"Next Moonset: {next_moonset.strftime('%Y-%m-%d %H:%M')}")
print(f"Current Moon Altitude: {get_moon_altaz(t)[0].degrees} degrees")
print(f"Current Moon Azimuth: {get_moon_altaz(t)[1].degrees} degrees")
print(f"Curent Moon Distance: {get_moon_altaz(t)[2].au} AU / {get_moon_altaz(t)[2].km} km")
print(f"Current Moon RA: {get_moon_ra_dec(t)[0]}")
print(f"Current Moon Declination: {get_moon_ra_dec(t)[1].dstr(places=1, warn=True, format=u'{0}{1}° {2:02}′ {3:02}.{4:0{5}}″')}")
print(f"Current Moon Phase Angle: {get_moon_phase_angle(t)} degrees")
print(f"Current Moon Illumination: {get_moon_illumination(t) * 100:.2f}%")