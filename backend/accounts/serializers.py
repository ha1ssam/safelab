"""Accounts app — Serializers."""

from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    is_supervisor = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "email", "first_name", "last_name",
            "role", "role_display", "is_supervisor",
            "institution", "registration_number",
            "is_active", "date_joined",
        )
        # `role` is read-only so users can't promote themselves via PATCH /auth/me/.
        read_only_fields = ("id", "role", "is_active", "date_joined", "role_display", "is_supervisor")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "email", "password", "first_name", "last_name",
            "institution", "registration_number",
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            email=attrs["email"].lower().strip(),
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Credenciais inválidas.")
        if not user.is_active:
            raise serializers.ValidationError("Conta desativada.")
        attrs["user"] = user
        return attrs
