from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _

from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        label=_("Confirm Password"), write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "password_confirm", "first_name", "last_name", "is_staff")
        read_only_fields = ("is_staff",)
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5, "style": {"input_type": "password"}},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match.")

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"), style={"input_type": "password"}
    )
    first_name = serializers.CharField(label=_("First name"), required=False)
    last_name = serializers.CharField(label=_("Last name"), required=False)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        first_name = attrs.get("first_name")
        last_name = attrs.get("last_name")

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = _("User account is disabled.")
                    raise serializers.ValidationError(msg, code="authorization")

                # Optionally, you can validate first_name and last_name if needed
                if first_name and user.first_name != first_name:
                    msg = _("First name does not match.")
                    raise serializers.ValidationError(msg, code="authorization")

                if last_name and user.last_name != last_name:
                    msg = _("Last name does not match.")
                    raise serializers.ValidationError(msg, code="authorization")
            else:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _("Must include 'email' and 'password'.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs