from rest_framework import serializers
from .models import Accidents, Lights

class AccidentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accidents
        fields = '__all__'

class LightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lights
        fields = '__all__'
