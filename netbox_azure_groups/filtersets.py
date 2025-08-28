import django_filters
from django.contrib.contenttypes.models import ContentType
from netbox.filtersets import NetBoxModelFilterSet
from .models import AzureGroup
# TODO: Update for new model structure
# from .models import ContactGroupMembership, DeviceGroupMembership


class AzureGroupFilterSet(NetBoxModelFilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    object_id = django_filters.CharFilter(lookup_expr='iexact')
    group_type = django_filters.MultipleChoiceFilter(
        choices=AzureGroup._meta.get_field('group_type').choices
    )
    mail = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = AzureGroup
        fields = [
            'id', 'name', 'object_id', 'group_type', 'mail',
            'is_security_enabled', 'is_mail_enabled', 'created_datetime'
        ]


# TODO: Update for new model structure
# class ContactGroupMembershipFilterSet(NetBoxModelFilterSet):
#     pass
# 
# class DeviceGroupMembershipFilterSet(NetBoxModelFilterSet):
#     pass