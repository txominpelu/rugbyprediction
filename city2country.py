import requests
import time
from repoze.lru import lru_cache


def city_url(city, country):
    #return "http://nominatim.openstreetmap.org/search?city=${city}&country={country}&format=json&addressdetails=1".format(city=city,country=country)
    return "https://maps.googleapis.com/maps/api/geocode/json?address={city}&components=country:{country},locality:{city}&key=AIzaSyC2afnOhaVzlp62fre_2ENAu5yNUFvNwlM".format(city=city,country=country)


@lru_cache(maxsize=500)
def city_exists(city, country):
    resp = requests.get(city_url(city, country)).json()
    return resp['status'] == 'OK'
    #return len(resp) > 0

def which_country(match):
    time.sleep(0.01)
    city = match['ground']
    country1 = match['team_name']
    country2 = match['rival_name']
    try:
        exists1 = city_exists(city, country1)
        exists2 = city_exists(city, country2)
    except ValueError as e:
        print "Error: {0}".format(e)
        return "unknown"
    if exists1:
            if not exists2:
                print "{0},{1},{2},{3}".format(country1,country2, city,country1)
                return country1
    elif exists2:
            print "{0},{1},{2},{3}".format(country1,country2, city,country2)
            return country2
    return "unknown"
