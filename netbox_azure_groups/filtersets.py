import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from .models import AzureGroup, GroupMembership, GroupOwnership


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
            'id', 'name', 'object_id', 'group_type', 'source', 'mail',
            'is_security_enabled', 'is_mail_enabled', 'azure_created'
        ]


class GroupMembershipFilterSet(NetBoxModelFilterSet):
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AzureGroup.objects.all(),
        label='Group'
    )
    contact_id = django_filters.ModelMultipleChoiceFilter(
        queryset=None,  # Will be set in __init__
        label='Contact'
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=None,  # Will be set in __init__
        label='Device'
    )
    membership_type = django_filters.MultipleChoiceFilter(
        choices=[
            ('direct', 'Direct Member'),
            ('nested', 'Via Nested Group'), 
            ('dynamic', 'Dynamic Rule Match'),
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from tenancy.models import Contact
        from dcim.models import Device
        self.filters['contact_id'].queryset = Contact.objects.all()
        self.filters['device_id'].queryset = Device.objects.all()

    class Meta:
        model = GroupMembership
        fields = ['id', 'group_id', 'contact_id', 'device_id', 'membership_type']


class GroupOwnershipFilterSet(NetBoxModelFilterSet):
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
        model = GroupOwnership
        fields = ['id', 'group_id', 'contact_id']