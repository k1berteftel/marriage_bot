import aiohttp
from aiohttp import ClientSession

from config_data.config import Config, load_config


config: Config = load_config()


async def get_city(longitude: float, latitude: float, locale: str | None) -> list | None:
    async with ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        params = {
            'apikey': config.yandex.api_key,
            'geocode': f'{longitude}, {latitude}',
            'kind': 'locality',
            'format': 'json',
            'lang': 'ru_RU' if (locale == 'ru' or not locale) else 'en_RU'
        }
        url = f'https://geocode-maps.yandex.ru/v1/'
        async with client.get(url=url, params=params) as resp:
            print(await resp.json())
            data = await resp.json()
    return _get_current_geo_data(data)


async def get_geo(city: str, locale: str):
    async with ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as client:
        params = {
            'apikey': config.yandex.api_key,
            'geocode': city,
            'kind': 'locality',
            'format': 'json',
            'lang': 'ru_RU' if (locale == 'ru' or not locale) else 'en_RU'
        }
        url = f'https://geocode-maps.yandex.ru/v1/'
        async with client.get(url=url, params=params) as resp:
            print(await resp.json())
            data = await resp.json()
    return _get_current_geo_data(data)


def _get_current_geo_data(data: dict) -> list | None:
    objects = data['response']['GeoObjectCollection'].get('featureMember')
    if not objects:
        return None
    point = objects[0]['GeoObject']['Point'].get('pos').split(' ')
    components = objects[0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['Components']
    name = ''
    for component in components:
        if component['kind'] == 'locality':
            name = component['name']
    if not name:
        return None
    return [name, [float(point[0]), float(point[1])]]
