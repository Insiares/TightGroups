from Meteo_API import get_meteo_data
from datetime import datetime


def format_datetime(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    dt = format_datetime(datetime(2024, 9, 3, 19, 45, 0))
    response = get_meteo_data(dt=dt)
    print(response)
