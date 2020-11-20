from rest_framework import serializers
from history.models import *
from users.models import UserDetail
from datetime import datetime


class ActionHistoryAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionHistory
        fields = ('__all__')

    def create(self, validated_data):
        validated_data['action_by'] = self.context['request'].user
        instance = ActionHistory.objects.create(**validated_data)
        return instance