from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = [
            "id",
            "email",
            "phone",
            "password",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": True,
                "min_length": 8,
            }
        }

    def validate_email(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError("Email is required.")

        return value

    def validate_phone(self, value):
        if value:
            value = value.strip()

            if not value.isdigit():
                raise serializers.ValidationError(
                    "Phone number must contain only digits."
                )

            if len(value) < 10 or len(value) > 15:
                raise serializers.ValidationError(
                    "Phone number must be between 10 and 15 digits."
                )

        return value

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)
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
