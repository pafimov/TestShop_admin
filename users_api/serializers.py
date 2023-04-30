from rest_framework import serializers

from users_api.models import UserFree

class UserFreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFree
        fields = ('name',
                  'telegram_id',
                  'telegram_username',
                  'sum_bought'
                  ) 