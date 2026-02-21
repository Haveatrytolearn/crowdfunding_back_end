from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        read_only_fields = (
            "is_staff",
            "is_superuser",
            "is_active",
            "groups",
            "user_permissions",
        )
        extra_kwargs = {'password': {'write_only': True}}

    
    #
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser(**validated_data)

        if password:
            user.set_password(password)

        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
    
class UserDetailSerializer(CustomUserSerializer):
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
