from astroplan import Observer, FixedTarget
from astropy.time import Time
import astropy.units as u

# Set up observer, target, and time
keck = Observer(longitude=49.65*u.deg, latitude=-1.62*u.deg, elevation=7*u.m)
time = Time('2024-08-28 00:55:00')

# Find rise time of Sirius at Keck nearest to `time`
rise_time = keck.sun_rise_time(time)
print(rise_time.iso)
