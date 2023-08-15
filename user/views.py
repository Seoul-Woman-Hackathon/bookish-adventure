from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User


@api_view(["POST"])
def signup(request):
    if request.method == "POST":
        data = request.data
        email = data["email"]

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "User with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hashed_password = make_password(data["password"])
        now = datetime.now()

        user = User(
            name=data["name"],
            email=email,
            birthdate=data["birthdate"],
            phonenum=data["phonenum"],
            password=hashed_password,
            created_at=now,
            updated_at=now,
        )
        user.save()
        return Response(
            {"message": "User created successfully"}, status=status.HTTP_201_CREATED
        )


@api_view(["POST"])
def login(request):
    if request.method == "POST":
        data = request.data
        user = authenticate(username=data["email"], password=data["password"])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    if request.method == "POST":
        request.auth.delete()
        return Response({"message": "Logged out successfully"})
