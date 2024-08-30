import numpy as np
from astropy.coordinates import get_body, get_body_barycentric, EarthLocation, AltAz, solar_system_ephemeris
from astropy.time import Time
import astropy.units as u
from datetime import datetime
import pytz

def get_location(lat, lon, height=0):
  """Returns an EarthLocation object for the given latitude, longitude, and height."""
  return EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=height*u.m)

def get_current_time(timezone):
  """Returns the current local time and UTC time for the given timezone."""
  local_time = datetime.now(tz=pytz.timezone(timezone))
  local_time_astropy = Time(local_time)
  utc_time = local_time.astimezone(pytz.utc)
  return local_time, local_time_astropy, utc_time

def get_moon_information(location, time):
  """Retrieves information about the Moon at the specified location and time."""
  with solar_system_ephemeris.set('builtin'):
    moon = get_body('moon', time, location=location)
    sun = get_body('sun', time, location=location)

    # Moon position
    ra = moon.ra
    dec = moon.dec
    ra_hms = ra.to_string(unit=u.hour, sep='hms', precision=1)
    dec_dms = dec.to_string(unit=u.deg, sep='dms', precision=0)

    # Moon distance
    distance_earth = moon.distance.to(u.km)
    distance_earth_au = distance_earth / 1.496e+8  # Convert to AU

    # Moon illumination
    elongation = sun.separation(moon)
    phase_angle = np.arccos(np.cos(elongation))

    # Moon phase
    phase = (1 + np.cos(phase_angle)) / 2

    # Moonrise and moonset
    altaz = AltAz(obstime=time, location=location)
    moon_altaz = moon.transform_to(altaz)
    moonrise = time + (12 - moon_altaz.alt.hour) * u.hour
    moonset = time + (24 - moon_altaz.alt.hour) * u.hour

    print(f"## Moon Information")
    print(f"- Local time: {time.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
    print(f"- RA: {ra} / {ra_hms}")
    print(f"- Dec: {dec} / {dec_dms}")
    print(f"- Distance (km): {distance_earth:.2f}")
    print(f"- Distance (AU): {distance_earth_au:.2f}")
    print(f"- Illumination: {phase:.2f}")
    print(f"- Moonrise: {moonrise}")
    print(f"- Moonset: {moonset}")

    print("---")

# Define your location (replace with your coordinates)
location = get_location(48.8566, 2.3522)  # Example location: Paris, France

# Get the current local time
local_time, local_time_astropy, utc_time = get_current_time("Europe/Paris")

# Get information about the Moon
get_moon_information(location, local_time_astropy)
