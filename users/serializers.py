from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.reverse import reverse
from django.utils.translation import ugettext_lazy as _

from core.serializers import DekontModelSerializer, AmountField
from currencies.fields import CurrencyField

from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    reporting_currency = CurrencyField(required=False)

    class Meta:
        model = User
        fields = ('email', 'password', 'reporting_currency')

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        user = self.Meta.model.objects.create_user(email, password, **validated_data)
        return user

class UserSerializer(DekontModelSerializer):
    balance_amount = AmountField()
    reporting_currency = CurrencyField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'balance_amount',
            'reporting_currency',
            'group',
            'approvers',
            'reporters',
            'is_group_admin'
        )
        admin_editable_fields = (
            'username',
            'is_group_admin',
            'approvers',
            'balance_amount',
        )
        admin_only_fields = (
            'approvers',
            'balance_amount'
        )
        extra_kwargs = {
            'approvers': {
                'read_only': False,
                'queryset': lambda field: field.root.instance.get_group_members()
            }
        }

    def to_internal_value(self, data):
        user = self.context['request'].user
        errors = {}

        internal_value = super().to_internal_value(data)

        if user != self.instance:
            # Admin can only modify some fields
            non_admin_fields = set(data.keys()) - set(self.Meta.admin_editable_fields)
            if non_admin_fields:
                raise PermissionDenied('Only the user may modify these fields: ' + ', '.join(non_admin_fields))

        if not user.is_group_admin:
            # Some fields may only be modified by an admin
            admin_only_fields = set(data.keys()) - set(self.Meta.admin_only_fields)
            if admin_only_fields:
                raise PermissionDenied('Only an admin may modify these fields: ' + ', '.join(admin_only_fields))

        # User may not un-admin themselves
        if 'is_group_admin' in data:
            if not user.is_group_admin:
                raise PermissionDenied("Only a group admin may modify these fields: is_group_admin")
            elif user == self.instance and user.is_group_admin and not internal_value['is_group_admin']:
                errors['is_group_admin'] = \
                    "You cannot unset yourself as admin. Instead, make somebody else in your group admin"

        if errors:
            raise serializers.ValidationError(errors)

        return internal_value


    def update(self, instance, validated_data):
        # Fields not set with setattr()
        password = validated_data.pop('password', None)
        approvers = validated_data.pop('approvers', [])

        # Update attributes
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        # Set password properly
        if password is not None:
            instance.set_password(password)

        instance.save()

        # Set approvers, if changed
        if set(instance.approvers.all()) != set(approvers):
            instance.approvers.clear()
            for approver in approvers:
                instance.add_approver(approver)

        # Transfer admin role
        current_user = self.context['request'].user
        if 'is_group_admin' in validated_data and current_user != instance:
            current_user.is_group_admin = False
            current_user.save()

        return instance

class UserPublicSerializer(UserSerializer):
    """
    A user serializer that contains only public fields.
    """
    class Meta(UserSerializer.Meta):
        fields = (
            'id',
            'username',
            'is_group_admin'
        )
