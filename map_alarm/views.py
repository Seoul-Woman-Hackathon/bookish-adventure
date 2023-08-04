# views.py

from django.http import JsonResponse
from django.contrib.gis.geos import GEOSGeometry, Point
from urllib.parse import urlencode, quote_plus
from .models import Accidents, Lights
import requests
import xmltodict
import json

serviceKeyDecoded = "9RY8CmSL7UQKCLU9pCbdmyY99NX3bVLENRuOONDYO9jqek29urc+15dvoFIg/rXD4q1VFdQh6o5ctlcDbbbC+g=="

def fetch_data_from_api(url, serviceKeyDecoded, siDo, type_, numOfRows, pageNo, guGuns):
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

            res = requests.get(url + queryParams)
            if res.status_code == 200:
                response_text = res.text

                try:
                    data = json.loads(response_text)
                except json.JSONDecodeError:
                    try:
                        data = xmltodict.parse(response_text)
                    except xmltodict.expat.ExpatError:
                        return JsonResponse({"message": "Failed to parse API response.", "status": "error"})

                if "items" in data and "item" in data["items"]:
                    items = data["items"]["item"]

                    for item in items:
                        geom_json = item["geom_json"]
                        name = item["spot_nm"]
                        region = GEOSGeometry(geom_json)

                        try:
                            polygon_obj, _ = Accidents.objects.get_or_create(name=name)
                            polygon_obj.region = region
                            polygon_obj.save()
                        except Accidents.DoesNotExist:
                            polygon_obj = Accidents(name=name, region=region)
                            polygon_obj.save()

            else:
                return JsonResponse({"message": "Failed to fetch data from the API.", "status": "error"})

    return True

def save_crosswalk_data(url, serviceKeyDecoded):
    url = "http://apis.data.go.kr/3190000/CrossWalkService/getCrossWalkList"

    params = {
        "serviceKey": serviceKeyDecoded,
        "pageNo": "1",
        "numOfRows": "1000",  # Set the number of rows you want to fetch
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        response_text = response.text
        if response_text:
            try:
                data = json.loads(response_text)
                if "body" in data:
                    crosswalks = data["body"]
                    for crosswalk in crosswalks:
                        try:
                            latitude = crosswalk["LAT"]
                            longitude = crosswalk["LOT"]
                            road_address = crosswalk["LCTN_ROAD_NM_ADDR"]

                            point = Point(longitude, latitude)

                            regions = Accidents.objects.filter(region__contains=point)
                            if regions.exists():
                                region = regions.first()
                                Lights.objects.get_or_create(
                                    latitude=latitude,
                                    longitude=longitude,
                                    name=road_address,
                                    accidents_idaccidents=region,
                                )

                        except KeyError:
                            pass

                return "Data saved successfully."
            except json.JSONDecodeError:
                return "Failed to parse API response as JSON."
        else:
            return "Empty response received from the API."
    else:
        return "Failed to fetch data from the API."

def fetch_data_from_apis(request):
    url_bohang = "http://apis.data.go.kr/B552061/frequentzoneChild/getRestFrequentzoneChild"
    url_schoolzone = "http://apis.data.go.kr/B552061/schoolzoneChild/getRestSchoolzoneChild"
    siDo = "11"
    type_ = "json"
    numOfRows = "100"
    pageNo = "1"

    guGuns = ["710", "590"]

    results = [
        fetch_data_from_api(url_bohang, serviceKeyDecoded, siDo, type_, numOfRows, pageNo, guGuns),
        #fetch_data_from_api(url_schoolzone, serviceKeyDecoded, siDo, type_, numOfRows, pageNo, guGuns),
        save_crosswalk_data("http://apis.data.go.kr/3190000/CrossWalkService/getCrossWalkList", serviceKeyDecoded),
    ]

    # Process the results if needed

    return JsonResponse({"message": "Data imported successfully.", "status": "success"})

def find_traffic_lights(request):
    if request.method == 'GET':
        # latitude = float(request.GET.get('latitude', 0))
        # longitude = float(request.GET.get('longitude', 0))
        latitude=37.5037158484
        longitude=126.9609764931
        # Create a Point object from the given latitude and longitude
        point = Point(longitude, latitude)

        # Query the 'Accidents' table to find the matching region polygon
        accident = Accidents.objects.filter(region__contains=point).first()

        if accident:
            # Get the traffic lights associated with the matching accident
            traffic_lights = Lights.objects.filter(accidents_idaccidents=accident.idaccidents)

            # Prepare the response in JSON format
            response_data = {
                'in_accident_region': True,
                'traffic_lights': [
                    {
                        'id':light.idlights,
                        'latitude': light.latitude,
                        'longitude': light.longitude,
                    }
                    for light in traffic_lights
                ]
            }
        else:
            # If no matching accident is found, return an empty list for traffic lights
            response_data = {
                'in_accident_region': False,
                'traffic_lights': []
            }

        return JsonResponse(response_data)

    # Handle other HTTP methods if needed
    return JsonResponse({'error': 'Invalid request method'}, status=400)
