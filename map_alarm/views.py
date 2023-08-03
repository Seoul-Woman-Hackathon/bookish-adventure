# views.py

from django.http import JsonResponse
from django.contrib.gis.geos import GEOSGeometry, Point
import asyncio
import aiohttp
from urllib.parse import urlencode,quote_plus
from asgiref.sync import sync_to_async
from .models import Accidents,Lights
import requests
from django.shortcuts import HttpResponse
import xmltodict
import json

serviceKeyDecoded = "+THWNzZCVM8HYbGFp8GV2CPZjPEqQ+SqehbMQoQDEmuW7lR9JNUYwJtx3tolZ39qkQVZg0JgKrf3GAsaluhhEg=="

async def fetch_data_from_api(session, url, serviceKeyDecoded, siDo, type_, numOfRows, pageNo, guGuns):
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

            async with session.get(url + queryParams) as res:
                if res.status == 200:
                    # Read the response content as text
                    response_text = await res.text()

                    try:
                        # Try parsing the response as JSON
                        data = json.loads(response_text)
                    except json.JSONDecodeError:
                        try:
                            # If parsing as JSON fails, try parsing as XML
                            data = xmltodict.parse(response_text)
                        except xmltodict.expat.ExpatError:
                            return JsonResponse({"message": "Failed to parse API response.", "status": "error"})

                    # Now data should contain the parsed response (either JSON or XML)
                    # Continue processing the data as before...
                    if "items" in data and "item" in data["items"]:
                        items = data["items"]["item"]

                        for item in items:
                            geom_json = item["geom_json"]
                            name = item["spot_nm"]
                            region = GEOSGeometry(geom_json)

                            try:
                                polygon_obj = await sync_to_async(Accidents.objects.get)(name=name)
                                polygon_obj.region = region
                                await sync_to_async(polygon_obj.save)()
                            except Accidents.DoesNotExist:
                                polygon_obj = await sync_to_async(Accidents)(name=name, region=region)
                                await sync_to_async(polygon_obj.save)()

                else:
                    return JsonResponse({"message": "Failed to fetch data from the API.", "status": "error"})

    return True

async def fetch_data_from_apis(request):
    url_bohang = "http://apis.data.go.kr/B552061/frequentzoneChild/getRestFrequentzoneChild"
    url_schoolzone = "http://apis.data.go.kr/B552061/schoolzoneChild/getRestSchoolzoneChild"
    siDo = "11"
    type_ = "json"
    numOfRows = "100"
    pageNo = "1"

    guGuns = ["710", "590"]

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_data_from_api(session, url_bohang, serviceKeyDecoded, siDo, type_, numOfRows, pageNo, guGuns),
            fetch_data_from_api(session, url_schoolzone, serviceKeyDecoded, siDo, type_, numOfRows, pageNo, guGuns)
        ]
        results = await asyncio.gather(*tasks)

    # Process the results if needed

    return JsonResponse({"message": "Data imported successfully.", "status": "success"})


def save_crosswalk_data(request):
    url = "http://apis.data.go.kr/3190000/CrossWalkService/getCrossWalkList"

    params = {
        "serviceKey": serviceKeyDecoded,
        "pageNo": "1",
        "numOfRows": "1000",  # Set the number of rows you want to fetch
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "body" in data:
            crosswalks = data["body"]
            for crosswalk in crosswalks:
                try:
                    latitude = crosswalk["LAT"]
                    longitude = crosswalk["LOT"]
                    road_address = crosswalk["LCTN_ROAD_NM_ADDR"]

                    # Convert latitude and longitude to a Point object
                    point = Point(longitude, latitude)

                    # Check if the point falls within any of the regions' polygons
                    regions = Accidents.objects.filter(region__contains=point)
                    if regions.exists():
                        # Get the first matching region (assuming there is only one)
                        region = regions.first()

                        # Check if the record with the given latitude and longitude already exists for the region
                        # If not, save it to the database
                        Lights.objects.get_or_create(
                            latitude=latitude,
                            longitude=longitude,
                            name=road_address,
                            accidents_idaccidents=region,
                        )

                except KeyError:
                    # Handle the case where the required fields are missing
                    pass

            return HttpResponse("Data saved successfully.")
        else:
            return HttpResponse("No data found in the response.")
    else:
        return HttpResponse("Failed to fetch data from the API.")
