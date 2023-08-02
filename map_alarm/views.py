# views.py

from django.http import JsonResponse
from django.contrib.gis.geos import GEOSGeometry
import asyncio
import aiohttp
from urllib.parse import urlencode,quote_plus
from asgiref.sync import sync_to_async
from .models import Accidents

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
                    data = await res.json()
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
    serviceKeyDecoded = "+THWNzZCVM8HYbGFp8GV2CPZjPEqQ+SqehbMQoQDEmuW7lR9JNUYwJtx3tolZ39qkQVZg0JgKrf3GAsaluhhEg=="
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
