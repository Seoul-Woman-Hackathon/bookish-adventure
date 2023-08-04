from django.urls import path
from . import views

urlpatterns = [
    path('', views.fetch_data_from_apis, name='fetch_data_from_apis'),
    path('detail/', views.find_traffic_lights, name='find_traffic_lights'),
]
