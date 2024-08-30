from astroplan import Observer, FixedTarget
from astropy.time import Time

# Set up observer, target, and time
keck = Observer.at_site("Keck")
sirius = FixedTarget.from_name("Sirius")
time = Time('2010-05-11 06:00:00')

# Find rise time of Sirius at Keck nearest to `time`
rise_time = keck.target_rise_time(time, sirius)
