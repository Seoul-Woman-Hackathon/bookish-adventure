from django.urls import path
from . import views
from .views import CountView, SignupView, LoginView, LogoutView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("count/<int:iduser>/", CountView.as_view(), name="count"),
]
