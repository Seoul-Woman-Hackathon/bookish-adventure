from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
from rest_framework.views import APIView


@csrf_exempt
def signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        birthdate = request.POST.get("birthdate")
        phonenum = request.POST.get("phonenum")
        name = request.POST.get("name")

        if User.objects.filter(email=email).exists():
            return JsonResponse({"message": "Email already exists"}, status=400)

        hashed_password = make_password(password)
        user = User(
            email=email,
            password=hashed_password,
            name=name,
            phonenum=phonenum,
            birthdate=birthdate,
        )
        user.save()
        return JsonResponse({"message": "Signup successful"}, status=201)
    else:
        return JsonResponse({"message": "Invalid request"}, status=400)


@csrf_exempt
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"message": "Login successful"})
        else:
            return JsonResponse({"message": "Login failed"}, status=401)
    else:
        return JsonResponse({"message": "Invalid request"}, status=400)


@csrf_exempt
def user_logout(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({"message": "Logout successful"})
    else:
        return JsonResponse({"message": "Invalid request"}, status=400)


class CountView(APIView):
    def get(self, request, iduser):
        try:
            count = User.objects.filter(iduser=iduser).count()
            return JsonResponse({"count": count})
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
