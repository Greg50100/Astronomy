from skyfield.api import N, W, load, wgs84, position_of_radec, load_constellation_map
from skyfield import almanac
from datetime import timedelta
import pytz

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

f_twilight = almanac.dark_twilight_day(eph, cherbourg)
times_twilight, events_twilight = almanac.find_discrete(t0, t1, f_twilight)

# Définir le fuseau horaire de Paris
paris_tz = pytz.timezone('Europe/Paris')

def nearest_minute(dt):
    return (dt + timedelta(seconds=30)).replace(second=0, microsecond=0)

def get_next_sunrise_sunset(t):

    # Calculer les heures de lever et de coucher du soleil
    f_sun = almanac.sunrise_sunset(eph, cherbourg)
    times_sun, events_sun = almanac.find_discrete(t0, t2, f_sun)

    next_sunrise = None
    next_sunset = None

    for t, e in zip(times_sun, events_sun):
        if t.utc_datetime() > dt:
            rounded_time = nearest_minute(t.utc_datetime())
            rounded_time_paris = rounded_time.astimezone(paris_tz)
            if e and next_sunrise is None:
                next_sunrise = rounded_time_paris.strftime('%Y-%m-%d %H:%M')
            elif not e and next_sunset is None:
                next_sunset = rounded_time_paris.strftime('%Y-%m-%d %H:%M')
            if next_sunrise and next_sunset:
                break

    return next_sunrise, next_sunset

def get_sun_altaz(t):
    astrometrics = cherbourg_observer.at(t).observe(eph['sun'])
    apparent = astrometrics.apparent()
    alt, az, d = apparent.altaz()
    return alt, az, d

def get_sun_ra_dec(t):
    astrometrics = cherbourg_observer.at(t).observe(eph['sun'])
    apparent = astrometrics.apparent()
    ra, dec, d = apparent.radec()
    return ra, dec, d

def get_min_sun_altitude(t):
    min_altitude = None
    min_time = None
    min_azimuth = None

    # Vérifier l'altitude du Soleil toutes les 1 minutes pendant 24 heures
    for minutes in range(0, 24 * 60, 1):
        t_check = t.utc_datetime() + timedelta(minutes=minutes)
        t_skyfield = ts.utc(t_check.year, t_check.month, t_check.day, t_check.hour, t_check.minute)
        alt, az, _ = get_sun_altaz(t_skyfield)
        if min_altitude is None or alt.degrees < min_altitude:
            min_altitude = alt.degrees
            min_time = t_check
            min_azimuth = az.degrees

    return min_time, min_azimuth, min_altitude

def get_max_sun_altitude(t):
    max_altitude = None
    max_time = None
    max_azimuth = None

    # Vérifier l'altitude du Soleil toutes les 1 minutes pendant 24 heures
    for minutes in range(0, 24 * 60, 1):
        t_check = t.utc_datetime() + timedelta(minutes=minutes)
        t_skyfield = ts.utc(t_check.year, t_check.month, t_check.day, t_check.hour, t_check.minute)
        alt, az, _ = get_sun_altaz(t_skyfield)
        if max_altitude is None or alt.degrees > max_altitude:
            max_altitude = alt.degrees
            max_time = t_check
            max_azimuth = az.degrees

    return max_time, max_azimuth, max_altitude

def get_twilight_times(t):

    twilight_times = {
        'astronomical': (None, None),
        'nautical': (None, None),
        'civil': (None, None),
        'day': (None, None),
        'night': (None, None)
    }

    for t, e in zip(times_twilight, events_twilight):
        rounded_time = nearest_minute(t.utc_datetime()).astimezone(paris_tz).strftime('%Y-%m-%d %H:%M')
        if e == 0:
            twilight_times['night'] = (rounded_time, twilight_times['night'][1])
        elif e == 1:
            twilight_times['astronomical'] = (rounded_time, twilight_times['astronomical'][1])
        elif e == 2:
            twilight_times['nautical'] = (rounded_time, twilight_times['nautical'][1])
        elif e == 3:
            twilight_times['civil'] = (rounded_time, twilight_times['civil'][1])
        elif e == 4:
            twilight_times['day'] = (rounded_time, twilight_times['day'][1])
        elif e == 5:
            twilight_times['civil'] = (twilight_times['civil'][0], rounded_time)
        elif e == 6:
            twilight_times['nautical'] = (twilight_times['nautical'][0], rounded_time)
        elif e == 7:
            twilight_times['astronomical'] = (twilight_times['astronomical'][0], rounded_time)
        elif e == 8:
            twilight_times['night'] = (twilight_times['night'][0], rounded_time)

    return twilight_times

def dawn_time(t, twilight_type, moment):
    index_map = {
        'astronomical_dusk': {'start': 0, 'end': 1},
        'nautical_dusk': {'start': 1, 'end': 2},
        'civil_dusk': {'start': 2, 'end': 3},
        'civil_dawn': {'start': 4, 'end': 5},
        'nautical_dawn': {'start': 5, 'end': 6},
        'astronomical_dawn': {'start': 6, 'end': 7}
    }
    index = index_map[twilight_type][moment]
    dawn_time = nearest_minute(times_twilight.utc_datetime()[index]).astimezone(paris_tz).strftime('%Y-%m-%d %H:%M')
    return dawn_time

def is_sun_above_altitude(t, altitude):
    alt, _, _ = get_sun_altaz(t)
    return alt.degrees > altitude

def twilight(t, altitude):
    return is_sun_above_altitude(t, altitude)

def get_sun_constellation(t):
    observer = cherbourg_observer
    astrometric = observer.at(t).observe(eph['sun'])
    apparent = astrometric.apparent()
    ra, dec, _ = apparent.radec()
    ra_hours = ra.hours
    dec_degrees = dec.degrees
    constellation_at = load_constellation_map()
    position = position_of_radec(ra_hours, dec_degrees)
    constellation = constellation_at(position)
    return constellation

# Exemple d'utilisation

next_sunrise, next_sunset = get_next_sunrise_sunset(t)
sun_altitude = get_sun_altaz(t)[0].degrees
sun_azimuth = get_sun_altaz(t)[1].degrees

sun_distance_km = get_sun_altaz(t)[2].km

min_time, min_azimuth, min_altitude = get_min_sun_altitude(t)
min_time_paris = min_time.astimezone(paris_tz).strftime('%Y-%m-%d %H:%M')
max_time, max_azimuth, max_altitude = get_max_sun_altitude(t)
max_time_paris = max_time.astimezone(paris_tz).strftime('%Y-%m-%d %H:%M')


print(f"Next Sunrise: {next_sunrise}")
print(f"Next Sunset: {next_sunset}")
print(f"Current Sun Altitude: {sun_altitude:.2f} degrees")
print(f"Current Sun Azimuth: {sun_azimuth:.2f} degrees")
print(f"Current Sun Distance: {get_sun_altaz(t)[2].au:.7f} AU / {sun_distance_km:.2f} km")
print(f"Current Sun RA: {get_sun_ra_dec(t)[0]}")
print(f"Current Sun Declination: {get_sun_ra_dec(t)[1].dstr(places=1, warn=True, format=u'{0}{1}° {2:02}′ {3:02}.{4:0{5}}″')}")
print(f"Minimum Sun Altitude Time: {min_time_paris}")
print(f"Minimum Sun Altitude: {min_altitude:.2f} degrees")
print(f"Minimum Sun Azimuth: {min_azimuth:.2f} degrees")
print(f"Maximum Sun Altitude Time: {max_time_paris}")
print(f"Maximum Sun Altitude: {max_altitude:.2f} degrees")
print(f"Maximum Sun Azimuth: {max_azimuth:.2f} degrees")
print(f"Is the Sun above -6 degrees? {twilight(t, -6)}")
print(f"Is the Sun above -12 degrees? {twilight(t, -12)}")
print(f"Is the Sun above -18 degrees? {twilight(t, -18)}")
print(f"Is the Sun above -4 degrees? {twilight(t, -4)}")
print(f"Is the Sun above 6 degrees? {twilight(t, 6)}")
print(f"Astronomical Dusk Start: {dawn_time(t, 'astronomical_dusk', 'start')}")
print(f"Astronomical Dusk End: {dawn_time(t, 'astronomical_dusk', 'end')}")
print(f"Nautical Dusk Start: {dawn_time(t, 'nautical_dusk', 'start')}")
print(f"Nautical Dusk End: {dawn_time(t, 'nautical_dusk', 'end')}")
print(f"Civil Dusk Start: {dawn_time(t, 'civil_dusk', 'start')}")
print(f"Civil Dusk End: {dawn_time(t, 'civil_dusk', 'end')}")
print(f"Civil Dawn Start: {dawn_time(t, 'civil_dawn', 'start')}")
print(f"Civil Dawn End: {dawn_time(t, 'civil_dawn', 'end')}")
print(f"Nautical Dawn Start: {dawn_time(t, 'nautical_dawn', 'start')}")
print(f"Nautical Dawn End: {dawn_time(t, 'nautical_dawn', 'end')}")
print(f"Astronomical Dawn Start: {dawn_time(t, 'astronomical_dawn', 'start')}")
print(f"Astronomical Dawn End: {dawn_time(t, 'astronomical_dawn', 'end')}")
print(f"Sun Constellation: {get_sun_constellation(t)}")
