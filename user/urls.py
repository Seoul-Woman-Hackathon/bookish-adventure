from django.urls import path
from . import views
from .views import CountView

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("count/<int:iduser>/", CountView.as_view(), name="count"),
]
