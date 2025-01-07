from Meteo.test_token import regen_token
from fastapi import HTTPException
import requests
import os 
from datetime import datetime
from geopy.geocoders import Nominatim
from loguru import logger
logger.add("./logs/meteo.log")


def get_current_time() -> str:
    dt = datetime.now()
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

def get_loc(user_input : str = "13800") -> tuple:
    geolocator = Nominatim(user_agent="my_app")
    user_loc = geolocator.geocode(user_input)
    latitude = user_loc.latitude
    longitude = user_loc.longitude 
    logger.info(f"Location OK from {user_input}")
    return (latitude, longitude)

def get_meteo_data(user_input : str = "13800", dt: str = get_current_time()):
    latitude, longitude = get_loc(user_input)
    api_key = regen_token()
    return_format = 'json'
    # request_format = 't_2m:C,relative_humidity_2m:p,sfc_pressure:Pa,wind_dir_FL10:d,wind_speed_FL10:kmh,wind_gusts_10m_1h:kmh'
    request_format = 't_2m:C,precip_1h:mm,msl_pressure:hPa,wind_speed_10m:ms,wind_dir_10m:d,wind_gusts_10m_1h:ms,weather_symbol_1h:idx'
    url = f'https://api.meteomatics.com/{dt}/{request_format}/{latitude},{longitude}/{return_format}/?access_token={api_key}'

    response = requests.get(url)
    logger.debug(f"Response status code: {response.status_code}"
                f"Response content: {response.content}")
    match response.status_code:
        case 200:
            logger.info("Meteo call sucessful")
            # Extract metrics from response json
            response = response.json()
            output = {
                "temp_C": response['data'][0]['coordinates'][0]['dates'][0]['value'],
                "precipitation": response['data'][1]['coordinates'][0]['dates'][0]['value'],
                "pressure": response['data'][2]['coordinates'][0]['dates'][0]['value'],
                "wind_speed": response['data'][3]['coordinates'][0]['dates'][0]['value'],
                "wind_dir": response['data'][4]['coordinates'][0]['dates'][0]['value'],
                "wind_gust": response['data'][5]['coordinates'][0]['dates'][0]['value'],
                "weather_symbol": response['data'][6]['coordinates'][0]['dates'][0]['value'],
            }
            logger.debug(f"Output : {output}")
            return output
        case _:
            logger.error("Meteo call failed")
            logger.error(f"Response status code: {response.status_code}")
            logger.error(f"Response content: {response.content}")
            raise HTTPException(status_code=500, detail="Meteo call failed")

if __name__ == '__main__':
    get_meteo_data()
