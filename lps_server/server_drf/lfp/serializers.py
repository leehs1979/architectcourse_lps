from rest_framework import serializers
from lfp.models import LogFileProcessor
from django.contrib.auth.models import User

class LogFileProcessorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LogFileProcessor
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'           