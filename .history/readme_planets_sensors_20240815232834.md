# Planets Sensor

Ce projet utilise les bibliothèques `astronomy-engine` et `paho.mqtt.client` pour surveiller les positions et les états des planètes du système solaire et publier ces informations via MQTT.

## Fonctionnalités

- Calcul des coordonnées équatoriales des planètes
- Calcul de l'élongation par rapport au Soleil
- Calcul de l'illumination des planètes
- Détermination de la constellation dans laquelle se trouve chaque planète
- Calcul de l'altitude et de l'azimut des planètes
- Détermination des heures de lever et de coucher des planètes
- Publication des données via MQTT

## Installation

1. Clonez ce dépôt.
2. Installez les dépendances nécessaires :
    ```bash
    pip install astronomy-engine paho-mqtt
    ```

## Utilisation

1. Configurez les paramètres MQTT dans le script.
2. Exécutez le script :
    ```bash
    python planets_sensor.py
    ```

## Bibliothèques Utilisées

- **astronomy-engine** : Une bibliothèque pour les calculs astronomiques précis. Plus d'informations peuvent être trouvées sur astronomy-engine.
- **paho-mqtt** : Une bibliothèque pour la communication MQTT.

## Contributeurs

- **Greg-au-riz** - Développeur principal

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

