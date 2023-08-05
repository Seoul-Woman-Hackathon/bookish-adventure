from django.http import JsonResponse
from django.contrib.gis.geos import GEOSGeometry, Point
from urllib.parse import urlencode, quote_plus
from .models import Accidents, Lights
import requests
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache

SERVICE_KEY_DECODED = "9RY8CmSL7UQKCLU9pCbdmyY99NX3bVLENRuOONDYO9jqek29urc+15dvoFIg/rXD4q1VFdQh6o5ctlcDbbbC+g=="
CROSSWALK_API_URL = "http://apis.data.go.kr/3190000/CrossWalkService/getCrossWalkList"
FREQUENT_ZONE_API_URL = "http://apis.data.go.kr/B552061/frequentzoneChild/getRestFrequentzoneChild"
SI_DO = "11"
TYPE_ = "json"
NUM_OF_ROWS = "100"
PAGE_NO = "1"
GU_GUNS = ["710", "590"]

# 기존의 fetch_data_from_api 함수를 수정하여 캐싱을 적용합니다.
def fetch_data_from_api(url, params):
    cache_key = f"api:{url}?{urlencode(params)}"
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        json_data = response.json()
        # 캐시 유효 기간을 설정하고 응답을 캐싱합니다.
        cache.set(cache_key, json_data, timeout=60 * 15)  # 15분간 유효한 캐시
        return json_data
    except (requests.RequestException, json.JSONDecodeError) as e:
        return None



def save_accident_regions(gu_guns, service_key_decoded):
    for gu_gun in gu_guns:
        for search_year_cd in range(2013, 2024):
            params = {
                "ServiceKey": service_key_decoded,
                "siDo": SI_DO,
                "guGun": gu_gun,
                "numOfRows": NUM_OF_ROWS,
                "pageNo": PAGE_NO,
                "type": TYPE_,
                "searchYearCd": search_year_cd
            }

            data = fetch_data_from_api(FREQUENT_ZONE_API_URL, params)
            if not data:
                continue

            for item in data.get("items", {}).get("item", []):
                geom_json = item.get("geom_json")
                name = item.get("spot_nm")
                region = GEOSGeometry(geom_json)

                existing_region = Accidents.objects.filter(name=name).first()
                if not existing_region:
                    polygon_obj, _ = Accidents.objects.get_or_create(name=name)
                    polygon_obj.region = region
                    polygon_obj.save()


def save_traffic_lights(crosswalk_params, service_key_decoded):
    crosswalk_data = fetch_data_from_api(CROSSWALK_API_URL, crosswalk_params)
    if not crosswalk_data:
        return

    for crosswalk in crosswalk_data.get("body", []):
        try:
            latitude = crosswalk["LAT"]
            longitude = crosswalk["LOT"]
            road_address = crosswalk["LCTN_ROAD_NM_ADDR"]
            point = Point(longitude, latitude)

            existing_light = Lights.objects.filter(latitude=latitude, longitude=longitude).first()
            regions = Accidents.objects.filter(region__contains=point)

            if not existing_light and regions.exists():
                region = regions.first()
                Lights.objects.get_or_create(
                    latitude=latitude,
                    longitude=longitude,
                    name=road_address,
                    accidents_idaccidents=region
                )
        except KeyError:
            pass


@api_view(['GET','POST'])
def fetch_and_save_data(request):
    crosswalk_params = {
        "serviceKey": SERVICE_KEY_DECODED,
        "pageNo": "1",
        "numOfRows": "1000",
    }

    save_accident_regions(GU_GUNS, SERVICE_KEY_DECODED)
    save_traffic_lights(crosswalk_params, SERVICE_KEY_DECODED)

    # latitude = float(request.GET.get('latitude', 0))
    # longitude = float(request.GET.get('longitude', 0))
    latitude=37.5036009524
    longitude=126.9609228327
    point = Point(longitude, latitude)
    accident = Accidents.objects.filter(region__contains=point).first()

    if accident:
        traffic_lights = Lights.objects.filter(accidents_idaccidents=accident.idaccidents)
        response_data = {
            'in_accident_region': True,
            'traffic_lights': [
                {
                    'latitude': light.latitude,
                    'longitude': light.longitude,
                }
                for light in traffic_lights
            ]
        }
    else:
        response_data = {
            'in_accident_region': False,
            'traffic_lights': []
        }

    return Response(response_data)
