from skyfield.api import load, Topos
from skyfield import almanac
from datetime import timedelta
import pytz

dt = t.utc_datetime()
t0 = ts.utc(dt.year, dt.month, dt.day)
t1 = ts.utc((dt + timedelta(days=1)).year, (dt + timedelta(days=1)).month, (dt + timedelta(days=1)).day)
t2 = ts.utc((dt + timedelta(days=2)).year, (dt + timedelta(days=2)).month, (dt + timedelta(days=2)).day)

eph = load('de421.bsp')
earth = eph['earth']
cherbourg = Topos('49.6386 N', '1.6163 W')  # Utilisation de Topos pour Cherbourg

# Définir le fuseau horaire de Paris
paris_tz = pytz.timezone('Europe/Paris')

def nearest_minute(dt):
    return (dt + timedelta(seconds=30)).replace(second=0, microsecond=0)

def get_next_moonrise_moonset(observer, t0, t1):
    moon = eph['moon']
    f = almanac.risings_and_settings(eph, moon, observer)
    t, y = almanac.find_discrete(t0, t1, f)
    next_moonrise = t[y][0].utc_datetime()
    next_moonset = t[y][1].utc_datetime()
    return next_moonrise, next_moonset

next_moonrise, next_moonset = get_next_moonrise_moonset(cherbourg, t0, t1)

print(f"Next Moonrise: {next_moonrise.astimezone(paris_tz)}")
print(f"Next Moonset: {next_moonset.astimezone(paris_tz)}")