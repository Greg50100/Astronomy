from skyfield.api import N, W, load, wgs84, PlanetaryConstants
from skyfield import almanac, eclipselib
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import pytz
from math import cos


# Charger les éphémérides et définir l'observateur
ts = load.timescale()
t = ts.now()
dt = t.utc_datetime()
t0 = ts.utc(dt.year, dt.month, dt.day)
t1 = ts.utc((dt + timedelta(days=1)).year, (dt + timedelta(days=1)).month, (dt + timedelta(days=1)).day)
t2 = ts.utc((dt + timedelta(days=2)).year, (dt + timedelta(days=2)).month, (dt + timedelta(days=2)).day)
t365 = ts.utc((dt + relativedelta(years=1)).year, (dt + relativedelta(years=1)).month, (dt + relativedelta(years=1)).day)

eph = load('de421.bsp')
earth = eph['earth']
moon = eph['moon']
cherbourg = wgs84.latlon(49.6386 * N, 1.6163 * W)  # Exemple de coordonnées pour Cherbourg
cherbourg_observer = earth + cherbourg


pc = PlanetaryConstants()
pc.read_text(load('moon_080317.tf'))
pc.read_text(load('pck00008.tpc'))
pc.read_binary(load('moon_pa_de421_1900-2050.bpc'))

frame = pc.build_frame_named('MOON_ME_DE421')

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
    astrometrics = cherbourg_observer.at(t).observe(moon)
    apparent_moon = astrometrics.apparent()
    astrometrics = cherbourg_observer.at(t).observe(sun)
    apparent_sun = astrometrics.apparent()
    return (1 + cos(apparent_moon.separation_from(apparent_sun).radians)) / 2

def get_moon_libration(t):
    p = (earth - moon).at(t)
    lat, lon, distance = p.frame_latlon(frame)
    lat_degrees = lat.degrees
    lon_degrees = (lon.degrees + 180.0) % 360.0 - 180.0
    return lon_degrees, lat_degrees

def get_min_moon_altitude(t):
    min_altitude = None
    min_time = None
    min_azimuth = None

    # Vérifier l'altitude de la Lune toutes les 1 minutes pendant 24 heures
    for minutes in range(0, 24 * 60, 1):
        t_check = t.utc_datetime() + timedelta(minutes=minutes)
        t_skyfield = ts.utc(t_check.year, t_check.month, t_check.day, t_check.hour, t_check.minute)
        alt, az, _ = get_moon_altaz(t_skyfield)
        if min_altitude is None or alt.degrees < min_altitude:
            min_altitude = alt.degrees
            min_time = t_check
            min_azimuth = az.degrees

    return min_time, min_azimuth, min_altitude

def get_max_moon_altitude(t):
    max_altitude = None
    max_time = None
    max_azimuth = None

    # Vérifier l'altitude de la Lune toutes les 1 minutes pendant 24 heures
    for minutes in range(0, 24 * 60, 1):
        t_check = t.utc_datetime() + timedelta(minutes=minutes)
        t_skyfield = ts.utc(t_check.year, t_check.month, t_check.day, t_check.hour, t_check.minute)
        alt, az, _ = get_moon_altaz(t_skyfield)
        if max_altitude is None or alt.degrees > max_altitude:
            max_altitude = alt.degrees
            max_time = t_check
            max_azimuth = az.degrees

    return max_time, max_azimuth, max_altitude

def get_moon_phase(t):
    phase_angle = get_moon_phase_angle(t)
    illumination = get_moon_illumination(t)
    if phase_angle < 45:
        return "New Moon"
    elif phase_angle < 135:
        if illumination < 0.5:
            return "First Quarter"
        else:
            return "Last Quarter"
    elif phase_angle < 225:
        return "Full Moon"
    else:
        if illumination < 0.5:
            return "Last Quarter"
        else:
            return "First Quarter"
        
def get_lunar_eclipse(t0, t365):
    t, y, details = eclipselib.lunar_eclipses(t0, t365, eph)  
    return t, y, details

next_moonrise, next_moonset = get_next_moonrise_moonset(cherbourg, t0, t2)

print(f"Next Moonrise: {next_moonrise.strftime('%Y-%m-%d %H:%M')}")
print(f"Next Moonset: {next_moonset.strftime('%Y-%m-%d %H:%M')}")
print(f"Current Moon Altitude: {get_moon_altaz(t)[0].degrees} degrees")
print(f"Current Moon Azimuth: {get_moon_altaz(t)[1].degrees} degrees")
print(f"Curent Moon Distance: {get_moon_altaz(t)[2].au} AU / {get_moon_altaz(t)[2].km} km")
print(f"Current Moon RA: {get_moon_ra_dec(t)[0]}")
print(f"Current Moon Declination: {get_moon_ra_dec(t)[1].dstr(places=1, warn=True, format=u'{0}{1}° {2:02}′ {3:02}.{4:0{5}}″')}")
print(f"Current Moon Phase Angle: {get_moon_phase_angle(t)} degrees")
print(f"Current Moon Illumination: {100-get_moon_illumination(t)*100:.2f}%")
print(f"Current Moon Libration Longitude: {get_moon_libration(t)[0]:.3f} degrees")
print(f"Current Moon Libration Latitude: {get_moon_libration(t)[1]:.3f} degrees")
# print(f"Minimum Moon Altitude: {get_min_moon_altitude(t0)[2]:.2f} degrees at {get_min_moon_altitude(t0)[0].strftime('%Y-%m-%d %H:%M')}")
# print(f"Maximum Moon Altitude: {get_max_moon_altitude(t0)[2]:.2f} degrees at {get_max_moon_altitude(t0)[0].strftime('%Y-%m-%d %H:%M')}")
print(f"Current Moon Phase: {get_moon_phase(t)}")
print(f"Next Lunar Eclipse: {get_lunar_eclipse(t0, t365)[0][1].utc_strftime('%Y-%m-%d %H:%M')}")



