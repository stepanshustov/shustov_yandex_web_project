from googletrans import Translator
import sqlite3
import requests
import datetime
from pprint import pprint
from config import *

LANGUAGES_ = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'ny': 'chichewa',
    'zh-tw': 'chinese',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'french',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'german',
    'el': 'greek',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'he': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'korean',
    'ku': 'kurdish',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mn': 'mongolian',
    'my': 'myanmar',
    'ne': 'nepali',
    'no': 'norwegian',
    'or': 'odia',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'gd': 'scots gaelic',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'ug': 'uyghur',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu'
}

LANGUAGES = dict()
for el in LANGUAGES_.keys():
    LANGUAGES[LANGUAGES_[el]] = el


def detect_lang(text: str):
    translator = Translator()
    src = translator.detect(text)
    return src.lang


def text_translator(text: str, dest='en') -> str:
    try:

        translator = Translator()
        src = translator.detect(text)
        translation = translator.translate(text=text, src=src.lang, dest=dest)

        return translation.text
    except Exception as ex:
        print(ex)
        return "Error"


class Users:
    def __init__(self, filename):
        self.con = sqlite3.connect(filename)
        self.cur = self.con.cursor()
        self.d = dict()
        for el in self.cur.execute("select id, language from users").fetchall():
            self.d[el[0]] = el[1]

    def all_users(self) -> dict:
        return self.d

    def is_user(self, user_id: int) -> bool:
        return user_id in self.d

    def __getitem__(self, item):
        return self.d[item]

    def add(self, user_id: int, lang: str):
        self.cur.execute(f"DELETE from users where id = {user_id}")
        self.con.commit()
        self.cur.execute(f"INSERT INTO users(id, language) VALUES({user_id}, '{lang}')")
        self.con.commit()
        self.d[user_id] = lang


code_to_smile = {
    "Clear": "Ясно \U00002600",
    "Clouds": "Облачно \U00002601",
    "Rain": "Дождь \U00002614",
    "Drizzle": "Дождь \U00002614",
    "Thunderstorm": "Гроза \U000026A1",
    "Snow": "Снег \U0001F328",
    "Mist": "Туман \U0001F32B"
}


def get_weather_of_json(js, toponym_address):
    temp = js['temp_c']
    windspd_ms = js['windspd_ms']
    wx_icon = js['wx_icon']
    winddir_compass = js['winddir_compass']
    wx_desc = js['wx_desc']
    st = f"""Погода в {toponym_address}.
    {wx_desc}
    Температура: {temp} C°
    Скорость ветра: {windspd_ms} метров/секунду
    Напрвление ветра: {winddir_compass}
    """
    return st, wx_icon


def weather(local: str):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={maps_token}&" \
                       f"geocode={local.strip()}&format=json"

    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()

        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        toponym_coodrinates = toponym["Point"]["pos"]
        coord = toponym_coodrinates.split()
        g = requests.get(
            f'http://api.weatherunlocked.com/api/current/{coord[0]},{coord[1]}?app_id={weather_app_id}&app_key={weather_app_key}&lang=ru')
        g2 = requests.get(
            f'http://api.weatherunlocked.com/api/forecast/{coord[0]},{coord[1]}?app_id={weather_app_id}&app_key={weather_app_key}&lang=ru')
        pprint(g2.json())
        return get_weather_of_json(g.json(), toponym_address)

    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        return "-1"


if __name__ == '__main__':
    weather(input())
