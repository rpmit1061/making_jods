from abc import ABCMeta

from rest_framework import serializers
from accounts import models as account_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = account_model.User
        exclude = ('created_at', 'updated_at', 'is_active',
                   'is_superuser', 'account_activation_token',
                   'last_login', 'groups', 'user_permissions')


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = account_model.User
        exclude = ('created_at', 'updated_at', 'is_active',
                   'is_superuser', 'account_activation_token',
                   'last_login', 'groups', 'user_permissions',
                   'is_staff', 'is_email_verify')


class ChangePasswordSerializer(serializers.Serializer):
    model = account_model.User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    otp = serializers.CharField(required=False)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = account_model.Profile
        exclude = ('created_at', 'updated_at')
