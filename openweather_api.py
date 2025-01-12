import httpx
from config import TOKEN
import json
import pandas as pd

URL_temp = "https://api.openweathermap.org/data/2.5/weather"
URL_geocode = "http://api.openweathermap.org/geo/1.0/direct"
city = "New York"
season = "winter"

df = pd.read_csv('data/temperature_data_processed.csv')
new_df = df[(df['city'] == city) & (df['season'] == season)].iloc[0]

data_geo = {
    "q": city,
    "appid": TOKEN
}

r_geocode = httpx.get(URL_geocode, params=data_geo)
resp_geo = json.loads(r_geocode.text)
lat = resp_geo[0]['lat']
lon = resp_geo[0]['lon']

data_temp = {
    "lat": lat,
    "lon": lon,
    "appid": TOKEN
}

r_temp = httpx.get(URL_temp, params=data_temp)
resp_temp = json.loads(r_temp.text)
temp = resp_temp['main']['temp']
temp_celsius = temp - 273.15

anomaly = (temp < (new_df['seasonal_mean'] - 2 * new_df['seasonal_std'])) | \
                    (new_df['temperature'] > (new_df['seasonal_mean'] + 2 * new_df['seasonal_std']))

print("Температура: ", temp_celsius)
print(anomaly)