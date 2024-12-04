
import requests
from requests.auth import HTTPBasicAuth
import os
from loguru import logger

logger.add("meteo.log")
# Replace with your actual username and password
username = os.getenv('meteo_use')
password = os.getenv('meteo_pwd')
# Make the GET request with basic authentication
if __name__ == "__main__":
    response = requests.get('https://login.meteomatics.com/api/v1/token', auth=HTTPBasicAuth(username, password))

# Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Extract the token from the response
        token = data.get('access_token')
        print('token:', token)
        with open('token.txt', 'w') as f:
            f.write(token)
    else:
        print('something went wrong:', response.status_code, response.text)
        

def regen_token():
    username = os.getenv('meteo_use')
    password = os.getenv('meteo_pwd')    
    logger.debug(f'username : {username} password : {password}') 
    response = requests.get('https://login.meteomatics.com/api/v1/token', auth=HTTPBasicAuth(username, password))
    
# Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        logger.info(f"Token regenerated")
        data = response.json()
        # Extract the token from the response
        token = data.get('access_token')
        print('token:', token)

        return token
    else:
       logger.error("meteo token error")
       logger.error(f"Response status code: {response.status_code}")
       logger.error(f"Response content: {response.content}")

