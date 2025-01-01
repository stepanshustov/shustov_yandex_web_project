
import sqlite3
import requests
import datetime
from pprint import pprint
from config import *
from datetime import datetime

WEEKDAY_LIST = ['Понедельник',
                'Вторник',
                'Среда',
                'Четверг',
                'Пятница',
                'Суббота',
                'Воскресенье'
                ]



def current_weather(local: str):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={maps_token}&" \
                       f"geocode={local.strip()}&format=json"

    response = requests.get(geocoder_request)
    try:
        json_response = response.json()

        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        toponym_coodrinates = toponym["Point"]["pos"]
        coord = toponym_coodrinates.split()
        g = requests.get(
            f'http://api.weatherunlocked.com/api/current/{coord[1]},{coord[0]}?app_id={weather_app_id}&app_key={weather_app_key}&lang=ru')
        js = g.json()
        temp = js['temp_c']
        windspd_ms = js['windspd_ms']
        wx_icon = js['wx_icon']
        winddir_compass = js['winddir_compass']
        wx_desc = js['wx_desc']
        st = f"""Погода в {toponym_address}.
        <b>{wx_desc}</b>
        <i>Температура:</i> <b>{temp} C°</b>
        <i>Скорость ветра:</i> <b>{windspd_ms} метров/секунду</b>
        <i>Напрвление ветра:</i> <b>{winddir_compass}</b>
        """
        return st, wx_icon


    except Exception:

        return "Проверьте правильность написания", ''


def forecast_weather(local: str):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={maps_token}&" \
                       f"geocode={local.strip()}&format=json"

    response = requests.get(geocoder_request)
    try:
        json_response = response.json()

        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        toponym_coodrinates = toponym["Point"]["pos"]
        coord = toponym_coodrinates.split()
        g = requests.get(
            f'http://api.weatherunlocked.com/api/forecast/{coord[1]},{coord[0]}?app_id={weather_app_id}&app_key={weather_app_key}&lang=ru')
        js = g.json()
        days = js['Days']
        ans = [f"""Погода в {toponym_address}."""]
        for elem in days:
            date = elem['date'].replace('/', '.')

            week_d = WEEKDAY_LIST[datetime.strptime(date, '%d.%m.%Y').date().weekday()]

            ans.append(f"""<b>{week_d}\t{date}</b>

<i>Температура:</i> <b>{elem['temp_min_c']} - {elem['temp_max_c']} °C</b>
<i>Ветер до</i> <b>{elem['windspd_max_ms']} метров/секунду</b>
<i>Рассвет</i> <b>{elem['sunrise_time']}</b>
<i>Закат</i> <b>{elem['sunset_time']}</b>
<i>Количество осадков</i> <b>{elem['precip_total_mm']}</b>""")

        return ans

    except Exception:
        return ["Проверьте правильность написания"]


if __name__ == '__main__':
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={maps_token}&" \
                       f"geocode={input().strip()}&format=json"

    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()

        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        toponym_coodrinates = toponym["Point"]["pos"]
        coord = toponym_coodrinates.split()
        g = requests.get(
            f'http://api.weatherunlocked.com/api/forecast/{coord[1]},{coord[0]}?app_id={weather_app_id}&app_key={weather_app_key}&lang=ru')
        pprint(g.json())
