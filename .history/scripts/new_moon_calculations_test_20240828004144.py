import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
import astropy.units as u
import astropy.time
import astropy.coordinates

# Save the time format we're using since
# scipy.optimize uses bare floats, but
# astropy needs to use astropy.time.Time
# instances
format_time = "jd"

def get_moon(
    t: float,
    location: astropy.coordinates.EarthLocation,
) -> float:
  """
  Compute the altitude and azimuth of the moon
  given a time and location.

  Parameters
  ----------
  t
    The current Julian day, expressed in UTC.
  location
    A point on the Earth
  """

  # Convert the given Julian Day into a Time object
  time = astropy.time.Time(t, format=format_time)
  # print(f"{time=}")

  # Load the coordinates of the Moon for the
  # given time.
  moon = astropy.coordinates.get_body(
      body="moon",
      time=time,
      location=location,
      ephemeris="de440",
  )

  # Define a topocentric coordinate frame
  # at the given time and location
  frame = astropy.coordinates.AltAz(
      location=location,
      obstime=time,
      pressure=1013.25 * u.mbar,
      temperature=15 * u.deg_C,
      obswl=550*u.nm,
  )

  # Transfrom the Moon's coordinates
  # into the topocentric frame
  moon = moon.transform_to(frame)

  return moon

def azimuth_moonset(
    time_guess: astropy.time.Time,
    location: astropy.coordinates.EarthLocation,
) -> u.Quantity:
  """
  Given a location and a guess for the time of moonrise/moonset, compute
  the azimuth of the Moon at the moment it's center of mass crosses the horizon.

  Parameters
  ----------
  time_guess
    The time at which to start the search
  location
    A point on the Earth.
  """

  # Save the dimensions of the location grid
  shape = location.shape

  # Loop over every point in the location grid
  result = np.empty(shape) << u.deg
  for index in np.ndindex(shape):

    # Isolate the current point in the location grid
    loc = location[index]

    # Define a function to find the root of
    def func(t: float):
      return get_moon(t, location[index]).alt.value

    # Compute the moment of moonrise/moonset
    t = scipy.optimize.root_scalar(
        f=func,
        x0=time_guess.to_value(format_time),
        x1=(time_guess + 10 * u.hr).to_value(format_time),
    ).root

    # Save the azimuth of the Moon at that moment
    result[index] = get_moon(t, loc).az

  return result

# Define a grid of locations on the Earth
lat = 45 * u.deg
lon = np.linspace(0, 100, num=11) * u.deg
location = astropy.coordinates.EarthLocation.from_geodetic(lat=lat, lon=lon)

# Compute the azimuth of the Moon
# at the moment of moonrise/moonset
az = azimuth_moonset(
    time_guess=astropy.time.Time("2025-07-03T17:30"),
    location=location
)

# Plot the result
fig, ax = plt.subplots()
ax.plot(lon, az);
ax.set_xlabel(f"longitude ({lon.unit:latex_inline})");
ax.set_ylabel(f"moonset azimuth ({az.unit:latex_inline})");