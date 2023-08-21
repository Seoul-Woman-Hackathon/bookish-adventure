from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import CustomToken

User = get_user_model()


class SignupView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        birthdate = request.data.get("birthdate")
        phonenum = request.data.get("phonenum")
        name = request.data.get("name")

        if not (email and password and birthdate and phonenum and name):
            return Response(
                {"message": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(email=email).exists():
            return Response(
                {"message": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create the user and set the password using the set_password method
        user = User(
            email=email,
            name=name,
            phonenum=phonenum,
            birthdate=birthdate,
        )
        user.set_password(password)
        user.save()

        # Create or retrieve the token associated with the user
        token, _ = CustomToken.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            token, _ = CustomToken.objects.get_or_create(user=user)
            return Response({"token": token.key, "message": "Login successful"})
        else:
            return Response(
                {"message": "Login failed"}, status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    def post(self, request):
        request.auth.delete()  # Delete the token associated with the current user
        return Response({"message": "Logout successful"})


class CountView(APIView):
    def get(self, request, iduser):
        try:
            user = User.objects.get(pk=iduser)
            count = User.objects.filter(iduser=iduser).count()
            return Response({"user": user.name, "count": count})
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
