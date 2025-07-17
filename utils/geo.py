from dadata import DadataAsync

from config_data.config import Config, load_config


config: Config = load_config()


async def get_city(longitude: float, latitude: float) -> list | None:
    dadata = DadataAsync(config.geolocator.api_key, config.geolocator.api_secret)
    result = await dadata.geolocate('address', lat=latitude, lon=longitude)
    print(result)
    if not result:
        return None
    data = result[0].get('data')
    if data.get('region_type_full') == 'город':
        city = data.get('region')
    elif data.get('settlement_type_full') == 'село':
        city = data.get('settlement')
    else:
        city = data.get('city')
    latitude = data.get('geo_lat')
    longitude = data.get('geo_lon')
    if not city or not latitude or not longitude:
        return None
    return [city, [longitude, latitude]]


async def get_geo(city: str):
    dadata = DadataAsync(config.geolocator.api_key, config.geolocator.api_secret)
    result = await dadata.clean('address', city)
    if result.get('region_type_full') == 'город':
        city = result.get('region')
    elif result.get('settlement_type_full') == 'село':
        city = result.get('settlement')
    else:
        city = result.get('city')
    latitude = result.get('geo_lat')
    longitude = result.get('geo_lon')
    if not city or not latitude or not longitude:
        return None
    return [city, [longitude, latitude]]




