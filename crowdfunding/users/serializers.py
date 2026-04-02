from rest_framework import serializers
from .models import CustomUser, UserChangeLog

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

# for admin interface
class UserChangeLogSerializer(serializers.ModelSerializer):
    changed_by_username = serializers.SerializerMethodField()

    class Meta:
        model = UserChangeLog
        fields = [
            "id",
            "field_name",
            "old_value",
            "new_value",
            "changed_at",
            "changed_by_username",
        ]

    def get_changed_by_username(self, obj):
        full_name = f"{obj.changed_by.first_name} {obj.changed_by.last_name}".strip()
        return full_name if full_name else obj.changed_by.username



class UserDetailSerializer(CustomUserSerializer):
    change_logs = UserChangeLogSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "change_logs",
        ]
        read_only_fields = ("is_active", "is_staff")

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance


class AdminUserSerializer(serializers.ModelSerializer):
    change_logs = UserChangeLogSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "change_logs",
        ]

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.is_staff = validated_data.get("is_staff", instance.is_staff)
        instance.save()
        return instance
    
# for admin interface