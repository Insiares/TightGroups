from datetime import datetime
from loguru import logger
import requests
from requests.auth import HTTPBasicAuth
from fastapi import HTTPException
import os
import dotenv
from geopy.geocoders import Nominatim


def regen_token():
    dotenv.load_dotenv()
    username = os.getenv("METEO_USERNAME")
    password = os.getenv("METEO_PWD")
    logger.debug(f"username : {username} password : {password}")
    response = requests.get(
        "https://login.meteomatics.com/api/v1/token",
        auth=HTTPBasicAuth(username, password),
    )

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        logger.info("Token regenerated")
        data = response.json()
        # Extract the token from the response
        token = data.get("access_token")
        print("token:", token)

        return token
    else:
        logger.error("meteo token error")
        logger.error(f"Response status code: {response.status_code}")
        logger.error(f"Response content: {response.content}")


def get_loc(user_input: str = "13800") -> tuple:
    geolocator = Nominatim(user_agent="my_app")
    user_loc = geolocator.geocode(user_input)
    latitude = user_loc.latitude
    longitude = user_loc.longitude
    logger.info(f"Location OK from {user_input}")
    return (latitude, longitude)


def get_meteo_data(user_input: str = "13800", dt: str = "2024-09-03T19:45:00Z"):
    latitude, longitude = get_loc(user_input)
    api_key = regen_token()
    return_format = "json"
    # request_format = 't_2m:C,relative_humidity_2m:p,sfc_pressure:Pa,wind_dir_FL10:d,wind_speed_FL10:kmh,wind_gusts_10m_1h:kmh'
    request_format = "t_2m:C,precip_1h:mm,msl_pressure:hPa,wind_speed_10m:ms,wind_dir_10m:d,wind_gusts_10m_1h:ms,weather_symbol_1h:idx"
    url = f"https://api.meteomatics.com/{dt}/{request_format}/{latitude},{longitude}/{return_format}/?access_token={api_key}"

    response = requests.get(url)
    logger.debug(
        f"Response status code: {response.status_code}"
        f"Response content: {response.content}"
    )
    match response.status_code:
        case 200:
            logger.info("Meteo call sucessful")
            response = response.json()
            output = {
                "temp_C": response["data"][0]["coordinates"][0]["dates"][0]["value"],
                "precipitation": response["data"][1]["coordinates"][0]["dates"][0][
                    "value"
                ],
                "pressure": response["data"][2]["coordinates"][0]["dates"][0]["value"],
                "wind_speed": response["data"][3]["coordinates"][0]["dates"][0][
                    "value"
                ],
                "wind_dir": response["data"][4]["coordinates"][0]["dates"][0]["value"],
                "wind_gust": response["data"][5]["coordinates"][0]["dates"][0]["value"],
                "weather_symbol": response["data"][6]["coordinates"][0]["dates"][0][
                    "value"
                ],  # I called symbol in hope to use it, but TODO
            }
            logger.debug(f"Output : {output}")
            return output
        case _:
            logger.error("Meteo call failed")
            logger.error(f"Response status code: {response.status_code}")
            logger.error(f"Response content: {response.content}")
            raise HTTPException(status_code=500, detail="Meteo call failed")


def format_datetime(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    dt = format_datetime(datetime(2024, 9, 3, 19, 45, 0))
    response = get_meteo_data(dt=dt)
    print(response)
