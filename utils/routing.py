import os
import staticmap
import requests
from database.models import Point
from config import load_geoapify_token


class RoutingMethods:
    api_key = load_geoapify_token()

    @classmethod
    def get_attractions(cls, points: list[list[str, str]]) -> list:
        pass

    @classmethod
    async def _get_coordinates(cls, points: list[Point], mode: str):
        points = [await cls.get_lat_lon_with_address(point.address) for point in points]
        points = '|'.join(','.join(map(str, point)) for point in points)
        url = (f'https://api.geoapify.com/v1/routing?waypoints={points}'
               f'&mode={mode}&apiKey={cls.api_key}')
        resp = requests.get(url)
        return resp.json()['features'][0]['geometry']['coordinates']

    @classmethod
    async def create_travel_map(cls, points: list[Point], mode: str, travel_id: int):
        travel_map = staticmap.StaticMap(width=800, height=400)
        coordinates = await cls._get_coordinates(points, mode)
        for coordinate in coordinates:
            line = staticmap.Line(coords=coordinate, width=2, color='blue')
            travel_map.add_line(line)
        file_path = os.getcwd()
        if not os.path.isdir('user_photos'):
            os.mkdir('user_photos')
        file_path = file_path + '\\user_photos\\' + str(travel_id) + '.png'
        image = travel_map.render()
        image.save(file_path, 'png')
        return file_path

    @classmethod
    async def get_lat_lon_with_address(cls, address: str) -> tuple[str, str] | bool:
        url = f'https://api.geoapify.com/v1/geocode/search?text={address}&limit=1&apiKey={cls.api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()["features"][0]
            latitude = result["geometry"]["coordinates"][1]
            longitude = result["geometry"]["coordinates"][0]
            return latitude, longitude
        return False

    @classmethod
    def get_time_in_travel(cls, lat: float, lon: float):
        pass
#
#
# RoutingMethods.create_travel_map([[56.7686, 54.1148], [56.666, 54.2000]], 'drive', 1)
