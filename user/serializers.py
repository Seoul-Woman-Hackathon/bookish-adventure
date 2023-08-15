from rest_framework import serializers
from .models import User  # 현재 앱의 모델을 임포트


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"  # 모든 필드를 포함하도록 설정
