from django.http import JsonResponse
from django.contrib.gis.geos import GEOSGeometry, Point
from urllib.parse import urlencode, quote_plus
from .models import Accidents, Lights
import requests
import json

serviceKeyDecoded = "9RY8CmSL7UQKCLU9pCbdmyY99NX3bVLENRuOONDYO9jqek29urc+15dvoFIg/rXD4q1VFdQh6o5ctlcDbbbC+g=="

def fetch_and_save_data(request):
    url_crosswalk = "http://apis.data.go.kr/3190000/CrossWalkService/getCrossWalkList"
    url_bohang = "http://apis.data.go.kr/B552061/frequentzoneChild/getRestFrequentzoneChild"
    siDo = "11"
    type_ = "json"
    numOfRows = "100"
    pageNo = "1"
    guGuns = ["710", "590"]

    # Fetch and save crosswalk data
    crosswalk_params = {
        "serviceKey": serviceKeyDecoded,
        "pageNo": "1",
        "numOfRows": "1000",
    }

    # Fetch and save traffic zone data
    for guGun in guGuns:
        for searchYearCd in range(2013, 2024):
            queryParams = '?' + urlencode({
                quote_plus('ServiceKey'): serviceKeyDecoded,
                quote_plus('siDo'): siDo,
                quote_plus('guGun'): guGun,
                quote_plus('numOfRows'): numOfRows,
                quote_plus('pageNo'): pageNo,
                quote_plus('type'): type_,
                quote_plus('searchYearCd'): searchYearCd
            })

            res = requests.get(url_bohang + queryParams)
            if res.status_code == 200:
                try:
                    data = res.json()
                    items = data.get("items", {}).get("item", [])
                    for item in items:
                        geom_json = item.get("geom_json")
                        name = item.get("spot_nm")
                        region = GEOSGeometry(geom_json)

                        # Check if the accident region with the same name exists in the database
                        existing_region = Accidents.objects.filter(name=name).first()

                        if not existing_region:
                            # If the region with the same name does not exist, create a new one
                            polygon_obj, _ = Accidents.objects.get_or_create(name=name)
                            polygon_obj.region = region
                            polygon_obj.save()
                except json.JSONDecodeError:
                    return JsonResponse({"message": "Failed to parse API response.", "status": "error"})
            else:
                return JsonResponse({"message": "Failed to fetch data from the API.", "status": "error"})
    crosswalk_response = requests.get(url_crosswalk, params=crosswalk_params)
    if crosswalk_response.status_code == 200:
        try:
            crosswalk_data = crosswalk_response.json()
            crosswalks = crosswalk_data.get("body", [])
            for crosswalk in crosswalks:
                try:
                    latitude = crosswalk["LAT"]
                    longitude = crosswalk["LOT"]
                    road_address = crosswalk["LCTN_ROAD_NM_ADDR"]
                    point = Point(longitude, latitude)

                    # Check if the traffic light with the same latitude and longitude exists in the database
                    existing_light = Lights.objects.filter(latitude=latitude, longitude=longitude).first()
                    regions = Accidents.objects.filter(region__contains=point)
                    if not existing_light and regions.exists():
                        region = regions.first()
                        Lights.objects.get_or_create(
                                    latitude=latitude,
                                    longitude=longitude,
                                    name=road_address,
                                    accidents_idaccidents=region)
                except KeyError:
                    pass
        except json.JSONDecodeError:
            return JsonResponse({"message": "Failed to parse API response as JSON.", "status": "error"})
    else:
        return JsonResponse({"message": "Failed to fetch data from the API.", "status": "error"})

    latitude = 37.5037158484
    longitude = 126.9609764931
    # latitude = float(request.GET.get('latitude', 0))
    # longitude = float(request.GET.get('longitude', 0))
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

    return JsonResponse(response_data)
