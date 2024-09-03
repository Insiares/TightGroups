import requests
import datetime
import os 
from test_token import regen_token


longitude : float =  43.515099 
latitude : float = 4.989500
# api_key : str | None= os.getenv("meteo_token")
api_key = regen_token()
print("token regenerated")
request_format : str = 't_2m:C'

return_format : str = 'json'

# get current time in iso 8601 format  like 2015-01-20T18:45Z
def get_current_time() -> str:
    dt = datetime.datetime.now()
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

dt = get_current_time()
# dt = '2024-09-03T19:45:00Z'
url = f'https://api.meteomatics.com/{dt}/{request_format}/{latitude},{longitude}/{return_format}/?access_token={api_key}'


response = requests.get(url)

match response.status_code:
    case 200:
        print('success')
        response = response.json()

        print(response['data'][0]['coordinates'][0]['dates'][0]['value'])
    case _:
        print('something went wrong')
        print(response.status_code)
        print(response.text)

# get value from response


# print(response['data']['value'])
