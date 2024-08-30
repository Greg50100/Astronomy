import time
import json
from skyfield.api import load, Topos
from skyfield.almanac import find_discrete, risings_and_settings, opposition_or_conjunction

# Charger les éphémérides
eph = load('de421.bsp')
ts = load.timescale()

# Obtenir la date actuelle
date = ts.now()

# Définir l'observateur à Cherbourg
observer = Topos(latitude_degrees=49.64, longitude_degrees=-1.62)

# Charger les données des planètes
planets = load('de421.bsp')
planet_names = ['mercury', 'venus', 'mars', 'jupiter barycenter', 'saturn barycenter', 'uranus barycenter', 'neptune barycenter', 'pluto barycenter']

def publish_planet_data():
    planet_data = {}
    for planet_name in planet_names:
        try:
            planet = planets[planet_name]
            
            # Calculer les coordonnées équatoriales
            astrometric = observer.at(date).observe(planet)
            ra, dec, distance = astrometric.radec()
            
            # Calculer l'élongation par rapport au Soleil
            elongation = astrometric.separation(planets['sun'])
            
            # Calculer l'illumination (approximation)
            phase_angle = astrometric.separation(planets['earth'])
            illumination = (1 + cos(phase_angle.radians)) / 2
            
            # Calculer la constellation
            constellation = astrometric.constellation()
            
            # Calculer l'altitude et l'azimut
            alt, az, _ = observer.at(date).observe(planet).apparent().altaz()
            
            # Trouver les heures de lever et de coucher
            t0, t1 = ts.utc(date.utc_datetime().year, date.utc_datetime().month, date.utc_datetime().day), ts.utc(date.utc_datetime().year, date.utc_datetime().month, date.utc_datetime().day + 1)
            f = risings_and_settings(eph, planet, observer)
            times, events = find_discrete(t0, t1, f)
            rise, set = None, None
            for ti, event in zip(times, events):
                if event == 1:
                    rise = ti.utc_iso()
                elif event == 0:
                    set = ti.utc_iso()
            
            # Calculer la conjonction ou l'opposition
            t, event = opposition_or_conjunction(eph, planet, observer)
            conjunction_type = "Conjonction" if event == 0 else "Opposition"
            
            # Ajouter les données de la planète
            planet_data[planet_name] = {
                "right_ascension": ra.hours,
                "declination": dec.degrees,
                "distance_au": distance.au,
                "elongation_degrees": elongation.degrees,
                "magnitude_apparente": illumination,
                "phase_angle": phase_angle.degrees,
                "constellation": constellation,
                "altitude_degrees": alt.degrees,
                "azimuth_degrees": az.degrees,
                "heure_de_lever": rise,
                "heure_de_coucher": set,
                "conjunction_type": conjunction_type,
                "state": "ON" if alt.degrees > 0 else "OFF"
            }
        except Exception as e:
            print(f"Error processing data for {planet_name}: {e}")
    
    return planet_data

while True:
    planet_data = publish_planet_data()
    print(json.dumps(planet_data, indent=4))  # Imprimer les données sous forme de chaîne JSON
    time.sleep(60)  # Attendre 60 secondes avant de répéter
