import astronomy
import paho.mqtt.client as mqtt
import json
import time

# Configurer MQTT
mqtt_client = mqtt.Client()
mqtt_client.connect("192.168.1.153", 1883, 60)
mqtt_client.username_pw_set("mqtt", "mqtt")

# Obtenir la date actuelle
date = astronomy.Time.Now()

# Définir l'observateur à Cherbourg
observer = astronomy.Observer(latitude=49.64, longitude=-1.62, height=0)

# Liste des planètes
planets = [astronomy.Body.Mercury, astronomy.Body.Venus, astronomy.Body.Mars, astronomy.Body.Jupiter, 
           astronomy.Body.Saturn, astronomy.Body.Uranus, astronomy.Body.Neptune, astronomy.Body.Pluto]

# Publier la disponibilité
mqtt_client.publish("homeassistant/binary_sensor/availability", "online")

def publish_planet_data():
    for planet in planets:
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

        # Déterminer l'état de visibilité
        state = "ON" if alt > 0 else "OFF"

        planet_name = planet.name.lower()
        
        config_payload = {
            "name": planet_name.capitalize(),
            "state_topic": f"homeassistant/binary_sensor/{planet_name}/state",
            "value_template": "{{ value_json.state }}",
            "json_attributes_topic": f"homeassistant/binary_sensor/{planet_name}/attributes",
            "json_attributes_template": "{{ value_json | tojson }}",
            "unique_id": f"binary_sensor_{planet_name}",
            "device": {
                "identifiers": ["planets_sensor"],
                "name": "Planets Sensor",
                "model": "Astronomy-Engine",
                "manufacturer": "Greg-au-riz"
            },
            "availability_topic": "homeassistant/binary_sensor/availability",
            "payload_available": "online",
            "payload_not_available": "offline"
        }

        state_payload = {
            "state": state
        }

        attributes_payload = {
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
            conjunction_type: str(inferior_conjunction if planet in [astronomy.Body.Mercury, astronomy.Body.Venus] else opposition),
            "conjonction_superieure": str(superior_conjunction),
            "perihelie": str(perihelion),
            "aphelie": str(aphelion)
        }

        mqtt_client.publish(f"homeassistant/binary_sensor/{planet_name}/config", json.dumps(config_payload))
        mqtt_client.publish(f"homeassistant/binary_sensor/{planet_name}/state", json.dumps(state_payload))
        mqtt_client.publish(f"homeassistant/binary_sensor/{planet_name}/attributes", json.dumps(attributes_payload))

while True:
    publish_planet_data()
    time.sleep(60)  # Attendre 60 secondes avant de répéter
