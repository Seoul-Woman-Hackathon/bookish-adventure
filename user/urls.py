from django.urls import path
from . import views
from .views import CountView

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("count/<int:iduser>/", CountView.as_view(), name="count"),
]
