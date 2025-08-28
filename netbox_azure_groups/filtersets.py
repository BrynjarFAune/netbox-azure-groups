import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from .models import AzureGroup, ContactGroupMembership, ContactGroupOwnership, DeviceGroupMembership


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


class ContactGroupMembershipFilterSet(NetBoxModelFilterSet):
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AzureGroup.objects.all(),
        label='Group'
    )
    contact_id = django_filters.ModelMultipleChoiceFilter(
        queryset=None,  # Will be set in __init__
        label='Contact'
    )
    member_type = django_filters.MultipleChoiceFilter(
        choices=ContactGroupMembership._meta.get_field('member_type').choices,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from tenancy.models import Contact
        self.filters['contact_id'].queryset = Contact.objects.all()

    class Meta:
        model = ContactGroupMembership
        fields = ['id', 'group_id', 'contact_id', 'member_type']


class DeviceGroupMembershipFilterSet(NetBoxModelFilterSet):
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AzureGroup.objects.all(),
        label='Group'
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=None,  # Will be set in __init__
        label='Device'
    )
    member_type = django_filters.MultipleChoiceFilter(
        choices=DeviceGroupMembership._meta.get_field('member_type').choices,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from dcim.models import Device
        self.filters['device_id'].queryset = Device.objects.all()

    class Meta:
        model = DeviceGroupMembership
        fields = ['id', 'group_id', 'device_id', 'member_type']


class ContactGroupOwnershipFilterSet(NetBoxModelFilterSet):
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AzureGroup.objects.all(),
        label='Group'
    )
    contact_id = django_filters.ModelMultipleChoiceFilter(
        queryset=None,  # Will be set in __init__
        label='Contact'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from tenancy.models import Contact
        self.filters['contact_id'].queryset = Contact.objects.all()

    class Meta:
        model = ContactGroupOwnership
        fields = ['id', 'group_id', 'contact_id']