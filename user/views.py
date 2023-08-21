from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User
from .serializers import UserSerializer
from rest_framework.views import APIView


@api_view(["POST"])
def signup(request):
    if request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "This email is already registered"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            password = serializer.validated_data["password"]
            user = serializer.save()
            user.set_password(password)  # Set the password explicitly
            user.save()  # Save the user object with the updated password

            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"token": token.key},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login_view(request):
    if request.method == "POST":
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})

        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    if request.method == "POST":
        request.auth.delete()  # Delete the token upon logout
        logout(request)
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )


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
