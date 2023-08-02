from django.urls import path
from . import views

urlpatterns = [
    path('', views.fetch_data_from_apis, name='fetch_data_from_apis'),
    path('detail/', views.save_crosswalk_data, name='save_crosswalk_data'),
]
