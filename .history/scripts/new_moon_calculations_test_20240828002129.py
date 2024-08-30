import numpy as np
from astropy.coordinates import get_body, EarthLocation, AltAz, solar_system_ephemeris, SkyCoord
from astropy.time import Time
import astropy.units as u
from datetime import datetime, timedelta
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

def get_moon_information(location, time, timezone):
  """Retrieves information about the Moon at the specified location and time."""
  with solar_system_ephemeris.set('de432s'):
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

    # Moon illumination (improved calculation)
    phase_angle = np.arccos((moon.earth_location.x - sun.earth_location.x) / moon.distance.to(u.au))
    phase = (1 + np.cos(phase_angle)) / 2

    # Moonrise and moonset (using iterative approach)
    altaz = AltAz(obstime=time, location=location)
    delta_t = 1 * u.minute  # Time step for iteration

    # Find moonrise
    t = time
    while altaz.alt.value < 0:
        t -= delta_t
        moon_altaz = moon.transform_to(AltAz(obstime=t, location=location))
    moonrise = t

    # Find moonset
    t = time
    while altaz.alt.value > 0:
        t += delta_t
        moon_altaz = moon.transform_to(AltAz(obstime=t, location=location))
    moonset = t

    print(f"## Moon Information")
    print(f"- Local time: {time.to_datetime(pytz.timezone(timezone)).strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
    print(f"- RA: {ra} / {ra_hms}")
    print(f"- Dec: {dec} / {dec_dms}")
    print(f"- Distance (km): {distance_earth:.2f}")
    print(f"- Distance (AU): {distance_earth_au:.2f}")
    print(f"- Illumination: {phase:.2f}")
    print(f"- Moonrise: {moonrise.iso}")  # Formatted for ISO standard
    print(f"- Moonset: {moonset.iso}")

    print("---")

# Define your location (replace with your coordinates)
location = get_location(49.6276, -1.6178)  # Example location: Unnamed

# Get the current local time
local_time, local_time_astropy, utc_time = get_current_time("CET")

# Get information about the Moon
get_moon_information(location, local_time_astropy, "CET")