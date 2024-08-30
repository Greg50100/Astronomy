import astronomy
import time
import json

# Obtenir la date actuelle
date = astronomy.Time.Now()

# Définir l'observateur à Cherbourg
observer = astronomy.Observer(latitude=49.64, longitude=-1.62, height=0)

# Liste des planètes
planets = [astronomy.Body.Mercury, astronomy.Body.Venus, astronomy.Body.Mars, 
           astronomy.Body.Jupiter, astronomy.Body.Saturn, astronomy.Body.Uranus, 
           astronomy.Body.Neptune, astronomy.Body.Pluto]

def publish_planet_data():
    planet_data = {}
    for planet in planets:
        try:
            # Calculer les coordonnées équatoriales
            equatorial = astronomy.Equator(planet, date, observer=observer, ofdate=True, aberration=True)
            
            # Calculer l'élongation par rapport au Soleil
            elongation_event = astronomy.Elongation(planet, date)
            
            # Calculer l'illumination
            illumination = astronomy.Illumination(planet, date)
            
            # Calculer la constellation
            constellation = astronomy.Constellation(equatorial.ra, equatorial.dec)
            
            # Calculer l'altitude et l'azimut
            horizon = astronomy.Horizon(date, observer, equatorial.ra, equatorial.dec, refraction=astronomy.Refraction.Normal)
            
            # Trouver les heures de lever et de coucher
            rise = astronomy.SearchRiseSet(planet, observer, astronomy.Direction.Rise, date, 1, 0)
            set = astronomy.SearchRiseSet(planet, observer, astronomy.Direction.Set, date, 1, 0)
            
            # Calculer la conjonction inférieure pour Mercure et Vénus
            if planet in [astronomy.Body.Mercury, astronomy.Body.Venus]:
                inferior_conjunction = astronomy.SearchRelativeLongitude(planet, 0.0, date)
                conjunction_type = "Conjonction inférieure"
            else:
                # Calculer l'opposition pour les autres planètes
                opposition = astronomy.SearchRelativeLongitude(planet, 180.0, date)
                conjunction_type = "Opposition"
            
            # Calculer la conjonction supérieure pour toutes les planètes
            superior_conjunction = astronomy.SearchRelativeLongitude(planet, 0.0, date)
            
            # Calculer le périhélie et l'aphélie
            apsis = astronomy.SearchPlanetApsis(planet, date)
            apsis2 = astronomy.NextPlanetApsis(planet, apsis)

            if apsis.dist_au > apsis2.dist_au:
                aphelion = apsis.time
                perihelion = apsis2.time
            else:
                aphelion = apsis2.time
                perihelion = apsis.time
            
            # Calculer l'altitude et l'azimut avec les conditions atmosphériques
            alt, az, distance = horizon.altitude, horizon.azimuth, equatorial.dist         

            state = "ON" if horizon.altitude > 0 else "OFF"
            
            # Ajouter les données de la planète
            planet_data[planet.name.lower()] = {
                "right_ascension": equatorial.ra,
                "declination": equatorial.dec,
                "distance_au": equatorial.dist,
                "elongation_degrees": elongation_event.elongation,
                "magnitude_apparente": illumination.mag,
                "phase_angle": illumination.phase_angle,
                "constellation": constellation.name,
                "altitude_degrees": alt,
                "azimuth_degrees": az,
                "heure_de_lever": str(rise),
                "heure_de_coucher": str(set),
                "conjunction_type": str(inferior_conjunction if planet in [astronomy.Body.Mercury, astronomy.Body.Venus] else opposition),
                "conjonction_superieure": str(superior_conjunction),
                "perihelie": str(perihelion),
                "aphelie": str(aphelion),
                "state": state
            }
        except Exception as e:
            print(f"Error processing data for {planet.name}: {e}")
    
    return planet_data

while True:
    planet_data = publish_planet_data()
    print(json.dumps(planet_data))  # Imprimer les données sous forme de chaîne JSON
    time.sleep(60)  # Attendre 60 secondes avant de répéter

