import django_filters
from django.contrib.contenttypes.models import ContentType
from netbox.filtersets import NetBoxModelFilterSet
from .models import AzureGroup, GroupMembership


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


class GroupMembershipFilterSet(NetBoxModelFilterSet):
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AzureGroup.objects.all(),
        label='Group'
    )
    member_type = django_filters.MultipleChoiceFilter(
        choices=[('direct', 'Direct'), ('nested', 'Nested')],
    )

    class Meta:
        model = GroupMembership
        fields = ['id', 'group_id', 'member_type']