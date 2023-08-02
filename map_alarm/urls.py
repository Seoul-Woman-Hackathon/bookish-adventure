from django.urls import path
from . import views

urlpatterns = [
    path('', views.bohang_db, name='bohang_db'),
    # path('/detail', views.detail, name='detail'),
]
