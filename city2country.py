import requests

def city_url(city, country):
    return "http://nominatim.openstreetmap.org/search?city=${city}&country={country}&format=json&addressdetails=1".format(city=city,country=country)

def city_exists(city, country):
    resp = requests.get(city_url(city, country)).json()
    return len(resp) > 0

def which_country(match):
    city = match['ground']
    country1 = match['team_name']
    country2 = match['rival_name']
    if city_exists(city, country1):
            if not city_exists(city, country2):
        	    return country1
    elif city_exists(city, country2):
            return country2
    return "unknown"
