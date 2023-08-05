# map_alarm/tasks.py

from celery import shared_task
from django.contrib.gis.geos import Point
from .models import Accidents, Lights
from .views import fetch_data_from_api, save_accident_regions, save_traffic_lights

@shared_task
def async_fetch_and_save_data():
    SERVICE_KEY_DECODED = "9RY8CmSL7UQKCLU9pCbdmyY99NX3bVLENRuOONDYO9jqek29urc+15dvoFIg/rXD4q1VFdQh6o5ctlcDbbbC+g=="
    CROSSWALK_API_URL = "http://apis.data.go.kr/3190000/CrossWalkService/getCrossWalkList"
    FREQUENT_ZONE_API_URL = "http://apis.data.go.kr/B552061/frequentzoneChild/getRestFrequentzoneChild"
    SI_DO = "11"
    TYPE_ = "json"
    NUM_OF_ROWS = "100"
    PAGE_NO = "1"
    GU_GUNS = ["710", "590"]

    crosswalk_params = {
        "serviceKey": SERVICE_KEY_DECODED,
        "pageNo": "1",
        "numOfRows": "1000",
    }

    save_accident_regions(GU_GUNS, SERVICE_KEY_DECODED)
    save_traffic_lights(crosswalk_params, SERVICE_KEY_DECODED)

    latitude = 37.5036009524
    longitude = 126.9609228327
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

    return response_data
