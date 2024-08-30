import numpy as np
from astropy.coordinates import get_body, get_body_barycentric, EarthLocation, AltAz, solar_system_ephemeris
from astropy.coordinates import get_constellation, SkyCoord
from poliastro.bodies import Sun, Earth, Mars, Jupiter, Saturn, Uranus, Neptune, Venus, Mercury
from poliastro.twobody import Orbit
from astropy.time import Time
import astropy.units as u
from datetime import datetime
import pytz
from astroquery.jplhorizons import Horizons

def get_location(lat, lon, height=0):
    """Returns an EarthLocation object for the given latitude, longitude, and height."""
    return EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=height*u.m)

def get_current_time(timezone):
    """Returns the current local time and UTC time for the given timezone."""
    local_time = datetime.now(tz=pytz.timezone(timezone))
    local_time_astropy = Time(local_time)
    utc_time = local_time.astimezone(pytz.utc)
    return local_time, local_time_astropy, utc_time

def get_barycentric_coordinates(planet, time):
    """Returns the barycentric coordinates of the given planet at the specified time."""
    with solar_system_ephemeris.set('builtin'):
        body_position = get_body_barycentric(planet, time)
    return body_position

def get_heliocentric_coordinates(planet, time):
    """Returns the heliocentric coordinates of the given planet at the specified time."""
    body_position = get_barycentric_coordinates(planet, time)
    sun_position = get_barycentric_coordinates('sun', time)
    heliocentric_coords = body_position - sun_position
    return heliocentric_coords.x, heliocentric_coords.y, heliocentric_coords.z

def get_geocentric_coordinates(planet, time):
    """Returns the geocentric coordinates of the given planet at the specified time."""
    body_position = get_barycentric_coordinates(planet, time)
    earth_position = get_barycentric_coordinates('earth', time)
    geocentric_coords = body_position - earth_position
    return geocentric_coords.x, geocentric_coords.y, geocentric_coords.z

def get_planet_ephemerides(id, time):
    """Returns the ephemerides of the given planet at the specified time."""
    obj = Horizons(id=id, location='500', epochs=time.jd)
    return obj.ephemerides()

def get_planet_rise_set_transit_times(body, location, time):
    """Returns the rise, set, and transit times of the given planet at the specified location and time."""
    delta_t = 1 * u.hour
    times = time + delta_t * np.arange(-12, 12, 0.1)
    body_altazs = body.transform_to(AltAz(obstime=times, location=location))
    body_rise = times[np.where(body_altazs.alt > 0)[0][0]]
    body_set = times[np.where(body_altazs.alt > 0)[0][-1]]
    body_transit = times[np.argmax(body_altazs.alt)]
    return body_rise, body_set, body_transit

def get_perihelion_aphelion_dates(planet, time):
    """Returns the perihelion and aphelion dates of the given planet."""
    start_date = Time(datetime.now(tz=pytz.timezone("Europe/Paris")))
    current_time_difference = (Time('2027-01-01') - Time('2024-08-01')).jd
    end_date = start_date + current_time_difference * u.day
    time_range = start_date + np.linspace(0, (end_date - start_date).jd, 1000) * u.day

    with solar_system_ephemeris.set('builtin'):
        body_positions = get_body_barycentric(planet, time_range)
        sun_positions = get_body_barycentric('sun', time_range)

    distances = np.linalg.norm(body_positions.xyz - sun_positions.xyz, axis=0)
    perihelion_index = np.argmin(distances)
    aphelion_index = np.argmax(distances)

    perihelion_date = time_range[perihelion_index]
    aphelion_date = time_range[aphelion_index]

    return perihelion_date, aphelion_date

def calculate_orbital_elements(body, time):
    """Calculates and returns the orbital elements of the given planet."""
    if body == 'mercury':
        planet = Mercury
    elif body == 'venus':
        planet = Venus
    elif body == 'mars':
        planet = Mars
    elif body == 'jupiter':
        planet = Jupiter
    elif body == 'saturn':
        planet = Saturn
    elif body == 'uranus':
        planet = Uranus
    elif body == 'neptune':
        planet = Neptune
    else:
        planet = Earth

    with solar_system_ephemeris.set('builtin'):
        r = get_body_barycentric(body, time).xyz.to(u.km)
        r_prev = get_body_barycentric(body, time - 1 * u.day).xyz.to(u.km)
        v = (r - r_prev) / (1 * u.day).to(u.s)

    orbit = Orbit.from_vectors(Sun, r, v, time)
    elements = {
        'semi_major_axis': orbit.a,
        'eccentricity': orbit.ecc,
        'inclination': orbit.inc,
        'longitude_of_ascending_node': orbit.raan,
        'argument_of_periapsis': orbit.argp,
        'true_anomaly': orbit.nu
    }
    return elements

def calculate_light_travel_time(distance_au):
    """Calculates and returns the light travel time for the given distance in AU."""
    speed_of_light_km_s = 299792.458
    distance_km = distance_au * 1.496e+8
    travel_time_seconds = distance_km / speed_of_light_km_s
    return travel_time_seconds / 3600  # Convert to hours

def calculate_distance_from_parallax(parallax_arcsec):
    """Calculates and returns the distance from the given parallax in arcseconds."""
    distance_parsecs = 1 / parallax_arcsec
    return distance_parsecs

def convert_to_galactic_coordinates(ra, dec):
    """Converts and returns the given RA and Dec to galactic coordinates."""
    coord = SkyCoord(ra=ra, dec=dec, frame='icrs')
    galactic_coord = coord.galactic
    return galactic_coord.l, galactic_coord.b

def calculate_angular_diameter(planet, distance_au):
    """Calculates and returns the angular diameter of the given planet at the specified distance."""
    planet_diameter_km = {
        'mercury': 4880,
        'venus': 12104,
        'mars': 6792,
        'jupiter': 142984,
        'saturn': 120536,
        'uranus': 51118,
        'neptune': 49528
    }
    
    # Vérifiez si la planète est dans le dictionnaire
    if planet not in planet_diameter_km:
        raise ValueError(f"Diameter for planet '{planet}' is not defined.")
    
    diameter_km = planet_diameter_km[planet]
    distance_km = distance_au * 1.496e+8  # Conversion de la distance de UA en kilomètres
    
    if distance_km == 0:
        raise ValueError("Distance cannot be zero.")
    
    angular_diameter_radians = diameter_km / distance_km
    angular_diameter_arcseconds = angular_diameter_radians * 206265
    return angular_diameter_arcseconds, planet_diameter_km

def get_planet_info(planet, time, location):
    """Calcule et retourne les informations d'une planète à un instant donné et un lieu donné.

    Args:
        planet (str): Le nom de la planète.
        time (astropy.time.Time): L'instant à considérer.
        location (astropy.coordinates.EarthLocation): Le lieu d'observation.

    Returns:
        dict: Un dictionnaire contenant les informations de la planète.
    """

    try:
        # Récupération des coordonnées barycentriques une seule fois
        body_position = get_body_barycentric(planet, time)
        sun_position = get_body_barycentric('sun', time)
        earth_position = get_body_barycentric('earth', time)

        # ... (le reste des calculs)

        # Vérification de l'observabilité
        body_altaz = body.transform_to(AltAz(obstime=time, location=location))
        is_observable = body_altaz.alt > 0 * u.deg

        return {
            # ... (les clés et valeurs du dictionnaire)
            'is_observable': is_observable
        }
    except Exception as e:
        print(f"Erreur lors du traitement de {planet}: {e}")
        return None

# Define the location of Cherbourg
cherbourg = get_location(49.65, -1.62)

# Get the current local time in Cherbourg
local_time, local_time_astropy, utc_time = get_current_time("Europe/Paris")

# List of main planets with their unique IDs
planets = {
    'mercury': '199',
    'venus': '299',
    'mars': '499',
    'jupiter': '599',
    'saturn': '699',
    'uranus': '799',
    'neptune': '899'
}

# Parallax values for each planet (in arcseconds)
parallax_values = {
    'mercury': 0.005,
    'venus': 0.01,
    'mars': 0.015,
    'jupiter': 0.002,
    'saturn': 0.001,
    'uranus': 0.0005,
    'neptune': 0.0003
}

# Get the information for each planet
# Utilisation de la fonction améliorée
for planet, id in planets.items():
  try:
    # Get planet information
    planet_info = get_planet_info(planet, local_time_astropy, cherbourg)
    if planet_info:
      # Display information if observable
      print(f"## {planet.capitalize()} Information")
      # ... (affichage des informations)
      if planet_info['is_observable']:
        print("La planète est actuellement observable à Cherbourg.")
      else:
        print("La planète n'est actuellement pas observable à Cherbourg.")

    # Définition de body AVANT son utilisation
    with solar_system_ephemeris.set('builtin'):
      body = get_body(planet, local_time_astropy, location=cherbourg)
      sun = get_body('sun', local_time_astropy, location=cherbourg)

      # ... (le reste des calculs utilisant body)

  except Exception as e:
    print(f"Erreur lors du traitement de {planet}: {e}")
    continue  # Passer à la planète suivante en cas d'erreur

    ra = body.ra
    dec = body.dec
    ra_hms = ra.to_string(unit=u.hour, sep='hms', precision=1)
    dec_dms = dec.to_string(unit=u.deg, sep='dms', precision=0)
    distance_au = body.distance.to(u.au)
    elongation = body.separation(sun)
    eph = get_planet_ephemerides(id, local_time_astropy)
    brightness = eph['V'][0]
    phase_angle = eph['alpha'][0]
    constellation = get_constellation(body)
    body_rise, body_set, body_transit = get_planet_rise_set_transit_times(body, cherbourg, local_time_astropy)
    body_rise_local = body_rise.to_datetime(timezone=pytz.timezone("Europe/Paris"))
    body_set_local = body_set.to_datetime(timezone=pytz.timezone("Europe/Paris"))
    body_transit_local = body_transit.to_datetime(timezone=pytz.timezone("Europe/Paris"))
    body_rise_altaz = body.transform_to(AltAz(obstime=body_rise, location=cherbourg))
    body_set_altaz = body.transform_to(AltAz(obstime=body_set, location=cherbourg))
    body_transit_altaz = body.transform_to(AltAz(obstime=body_transit, location=cherbourg))
    body_current_altaz = body.transform_to(AltAz(obstime=local_time_astropy, location=cherbourg))
    perihelion_date, aphelion_date = get_perihelion_aphelion_dates(planet, local_time_astropy)
    hx, hy, hz = get_heliocentric_coordinates(planet, local_time_astropy)
    gx, gy, gz = get_geocentric_coordinates(planet, local_time_astropy)

    # Calculate orbital elements
    orbital_elements = calculate_orbital_elements(planet, local_time_astropy)

    # Calculate light travel time
    light_travel_time_hours = calculate_light_travel_time(distance_au)

    # Get the parallax for the current planet
    parallax_arcsec = parallax_values[planet]
    
    # Calculate distance in parsecs using the parallax value
    distance_parsecs = calculate_distance_from_parallax(parallax_arcsec)

    # Convert to galactic coordinates
    galactic_l, galactic_b = convert_to_galactic_coordinates(ra, dec)


    # Calculate angular diameter
    angular_diameter_arcseconds, planet_diameter_km = calculate_angular_diameter(planet, distance_au)

    # Convert to value and print
    angular_diameter_value = angular_diameter_arcseconds
    print(f"- Angular diameter: {angular_diameter_value:.2f} arcseconds")

    print(f"## {planet.capitalize()} Information")
    print(f"### Summary")
    print(f"- Planet: {planet.capitalize()}")
    print(f"- Distance (AU): {distance_au:.2f}")
    print(f"- Distance (parsecs): {distance_parsecs:.2f}")
    print(f"- Brightness: {brightness}")
    print(f"- Constellation: {constellation}")
    print(f"- Rise: {body_rise_local}")
    print(f"- Set: {body_set_local}")
    print(f"- Transit: {body_transit_local}")
    print("### Observations")
    print(f"- Altitude at Rise: {body_rise_altaz.alt}")
    print(f"- Azimuth at Rise: {body_rise_altaz.az}")
    print(f"- Altitude at Set: {body_set_altaz.alt}")
    print(f"- Azimuth at Set: {body_set_altaz.az}")
    print(f"- Altitude at Transit: {body_transit_altaz.alt}")
    print(f"- Azimuth at Transit: {body_transit_altaz.az}")
    print(f"- Current Altitude: {body_current_altaz.alt}")
    print(f"- Current Azimuth: {body_current_altaz.az}")
    print("### Ephemerides")
    print(f"- Local time: {local_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
    print(f"- UTC time: {utc_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
    print(f"- RA: {ra} / {ra_hms}")
    print(f"- Dec: {dec} / {dec_dms}")
    print(f"- Elongation: {elongation}")
    print(f"- Phase Angle: {phase_angle}°")
    print(f"- Perihelion: {perihelion_date.iso}")
    print(f"- Aphelion: {aphelion_date.iso}")
    print("### Orbital Elements:")
    print(f"- Semi-major axis (a): {orbital_elements['semi_major_axis']}")
    print(f"- Eccentricity (e): {orbital_elements['eccentricity']}")
    print(f"- Inclination (i): {orbital_elements['inclination']}")
    print(f"- Longitude of ascending node (Ω): {orbital_elements['longitude_of_ascending_node']}")
    print(f"- Argument of periapsis (ω): {orbital_elements['argument_of_periapsis']}")
    print(f"- True anomaly (ν): {orbital_elements['true_anomaly']}")
    print("### Additional Information")
    print(f"- Heliocentric (hx, hy, hz): ({hx:.2f}, {hy:.2f}, {hz:.2f})")
    print(f"- Geocentric (gx, gy, gz): ({gx:.2f}, {gy:.2f}, {gz:.2f})")
    print(f"- Light travel time (hours): {light_travel_time_hours:.2f}")
    print(f"- Galactic coordinates: l={galactic_l:.2f}, b={galactic_b:.2f}")
    print(f"- Angular diameter: {angular_diameter_arcseconds:.2f} arcseconds")
    print(f"- Planet diameter (km): {planet_diameter_km.get(planet, 'Not found')}")
    print("---")