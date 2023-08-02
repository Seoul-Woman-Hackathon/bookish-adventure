# views.py

import json, requests
from urllib.parse import urlencode, quote_plus
from django.http import HttpResponse
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Polygon, MultiPolygon

from .models import Accidents

def bohang_db(request):
    # Update the serviceKeyDecoded variable with your actual API key
    serviceKeyDecoded = "+THWNzZCVM8HYbGFp8GV2CPZjPEqQ+SqehbMQoQDEmuW7lR9JNUYwJtx3tolZ39qkQVZg0JgKrf3GAsaluhhEg=="

    url = "http://apis.data.go.kr/B552061/frequentzoneChild/getRestFrequentzoneChild"
    siDo = "11"
    guGun = "710"
    searchYearCd = "2019"
    type_ = "json"
    numOfRows = "100"
    pageNo = "1"

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
    data = res.json()

    for item in data['items']['item']:
        # Get the JSON data for the polygon
        polygon_json = item['geom_json']

        # Load the JSON data to a Python dictionary
        polygon_data = json.loads(polygon_json)

        # Extract the coordinates from the JSON data
        coordinates = polygon_data['coordinates'][0]

        # Convert the coordinates to a Polygon object
        region = Polygon(coordinates)
        print(region)
        # Save the data to the database
        spot_name = item['spot_nm']
        accident = Accidents(region=region.wkt, name=spot_name)
        accident.save()


    # Return a response to indicate that the data has been fetched and saved
    return HttpResponse("Data fetched and saved successfully.")
