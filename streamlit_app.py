import streamlit as st
import pandas as pd
from pathlib import Path
import json
import httpx

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Temperature data',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_temp_data():
    """Grab temperature data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/temperature_data_processed.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 2010
    MAX_YEAR = 2019

    raw_gdp_df['timestamp'] = pd.to_datetime(raw_gdp_df['timestamp'])

    return raw_gdp_df

temp_df = get_temp_data()

'''
# :earth_americas: Temperature data

Исследуй исторические температурные данные.
'''
st.dataframe(temp_df.head(5))

min_value = temp_df['timestamp'].dt.year.min()
max_value = temp_df['timestamp'].dt.year.max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

cities = temp_df['city'].unique()

if not len(cities):
    st.warning("Select at least one city")

selected_cities = st.multiselect(
    'Which cities would you like to view?',
    cities,
    ['New York'])

# Filter the data
filtered_gdp_df = temp_df[
    (temp_df['city'].isin(selected_cities))
    & (temp_df['timestamp'].dt.year <= to_year)
    & (from_year <= temp_df['timestamp'].dt.year)
]

st.header('Temperature over time', divider='gray')

st.line_chart(
    filtered_gdp_df,
    x='timestamp',
    y='temperature',
    color='city',
)

if st.checkbox("Показать среднюю температуру по сезонам"):
    st.line_chart(
        filtered_gdp_df,
        x='timestamp',
        y='seasonal_mean',
        color='city',
    )

if st.checkbox("Показать среднее стандартное отклонение"):
    st.line_chart(
        filtered_gdp_df,
        x='timestamp',
        y='seasonal_std',
        color='city',
    )


API_TOKEN = st.text_input("Введите API  API-ключа OpenWeatherMap")

if len(API_TOKEN) > 0:
    try:
        URL_temp = "https://api.openweathermap.org/data/2.5/weather"
        URL_geocode = "http://api.openweathermap.org/geo/1.0/direct"
        season = "winter"

        for city in selected_cities:
            new_df = filtered_gdp_df[(filtered_gdp_df['city'] == city) & (filtered_gdp_df['season'] == season)].iloc[0]
            data_geo = {
                "q": city,
                "appid": API_TOKEN
            }

            r_geocode = httpx.get(URL_geocode, params=data_geo)
            resp_geo = json.loads(r_geocode.text)
            lat = resp_geo[0]['lat']
            lon = resp_geo[0]['lon']

            data_temp = {
                "lat": lat,
                "lon": lon,
                "appid": API_TOKEN
            }

            r_temp = httpx.get(URL_temp, params=data_temp)
            resp_temp = json.loads(r_temp.text)
            temp = resp_temp['main']['temp']
            temp_celsius = temp - 273.15

            anomaly = (temp < (new_df['seasonal_mean'] - 2 * new_df['seasonal_std'])) | \
                                (new_df['temperature'] > (new_df['seasonal_mean'] + 2 * new_df['seasonal_std']))

            st.subheader(city)
            st.write("Температура: ", round(temp_celsius, 2))
            if anomaly == True:
                st.write("Это аномальная температура")
            else:
                st.write("Это нормальная температура")
    except Exception as e:
        st.error("cod:401, message: Invalid API key. Please see https://openweathermap.org/faq#error401 for more info.")