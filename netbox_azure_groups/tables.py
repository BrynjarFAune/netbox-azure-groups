import django_tables2 as tables
from netbox.tables import BaseTable, ChoiceFieldColumn
from .models import AzureGroup, ProtectedResource, AccessControlMethod, FortiGatePolicy, AccessGrant


class AzureGroupTable(BaseTable):
    id = tables.Column(verbose_name='ID')
    name = tables.Column(
        verbose_name='Name',
        linkify=lambda record: record.get_absolute_url()
    )
    source = ChoiceFieldColumn()
    group_type = ChoiceFieldColumn() 
    member_count = tables.Column(verbose_name='Members')
    object_id = tables.Column(verbose_name='Azure ID', attrs={'td': {'class': 'font-monospace'}})

    class Meta(BaseTable.Meta):
        model = AzureGroup
        fields = ('id', 'name', 'object_id', 'source', 'group_type', 'member_count', 'description')
        default_columns = ('id', 'name', 'object_id', 'source', 'group_type', 'member_count')
        # Explicitly exclude actions and selection columns
        exclude = ('pk',)
        
    # Override to prevent automatic action column generation
    def __init__(self, *args, **kwargs):
        # Remove any automatic columns that might cause edit URL issues
        super().__init__(*args, **kwargs)
        # Remove any columns that might try to generate edit URLs
        if hasattr(self.base_columns, 'actions'):
            del self.base_columns['actions']


class ProtectedResourceTable(BaseTable):
    id = tables.Column(verbose_name='ID')
    name = tables.Column(
        verbose_name='Name',
        linkify=lambda record: record.get_absolute_url()
    )
    resource_type = ChoiceFieldColumn()
    criticality = ChoiceFieldColumn()
    owner_contact = tables.Column(verbose_name='Owner')
    is_active = tables.BooleanColumn(verbose_name='Active')
    access_method_count = tables.Column(verbose_name='Access Methods', empty_values=())
    grant_count = tables.Column(verbose_name='Access Grants', empty_values=())

    class Meta(BaseTable.Meta):
        model = ProtectedResource
        fields = (
            'id', 'name', 'resource_type', 'criticality', 
            'owner_contact', 'is_active', 'access_method_count', 'grant_count'
        )
        default_columns = (
            'id', 'name', 'resource_type', 'criticality', 
            'is_active', 'access_method_count', 'grant_count'
        )


class AccessControlMethodTable(BaseTable):
    id = tables.Column(verbose_name='ID')
    name = tables.Column(
        verbose_name='Name',
        linkify=lambda record: record.get_absolute_url()
    )
    resource = tables.Column(
        verbose_name='Protected Resource',
        linkify=lambda record: record.resource.get_absolute_url() if record.resource else None
    )
    control_type = ChoiceFieldColumn()
    azure_group = tables.Column(
        verbose_name='Azure Group',
        linkify=lambda record: record.azure_group.get_absolute_url() if record.azure_group else None
    )
    access_level = ChoiceFieldColumn()
    is_active = tables.BooleanColumn(verbose_name='Active')
    grant_count = tables.Column(verbose_name='Access Grants', empty_values=())
    last_verified = tables.DateTimeColumn(verbose_name='Last Verified')

    class Meta(BaseTable.Meta):
        model = AccessControlMethod
        fields = (
            'id', 'name', 'resource', 'control_type', 'azure_group', 
            'access_level', 'is_active', 'grant_count', 'last_verified'
        )
        default_columns = (
            'id', 'name', 'resource', 'control_type', 'azure_group', 
            'access_level', 'is_active', 'grant_count'
        )


class FortiGatePolicyTable(BaseTable):
    policy_id = tables.Column(
        verbose_name='Policy ID',
        linkify=lambda record: record.get_absolute_url()
    )
    name = tables.Column(verbose_name='Name')
    action = ChoiceFieldColumn()
    status = ChoiceFieldColumn()
    source_interfaces_display = tables.Column(verbose_name='Source', accessor='source_interfaces_display')
    destination_interfaces_display = tables.Column(verbose_name='Destination', accessor='destination_interfaces_display')
    services_display = tables.Column(verbose_name='Services', accessor='services_display')
    nat_enabled = tables.BooleanColumn(verbose_name='NAT')
    utm_status = ChoiceFieldColumn(verbose_name='UTM')
    ai_description = tables.Column(
        verbose_name='Description', 
        attrs={'td': {'class': 'text-truncate', 'style': 'max-width: 300px;'}},
        orderable=False
    )

    class Meta(BaseTable.Meta):
        model = FortiGatePolicy
        fields = (
            'policy_id', 'name', 'action', 'status', 
            'source_interfaces_display', 'destination_interfaces_display', 'services_display',
            'nat_enabled', 'utm_status', 'ai_description'
        )
        default_columns = (
            'policy_id', 'name', 'action', 'status', 
            'source_interfaces_display', 'destination_interfaces_display', 
            'nat_enabled', 'ai_description'
        )


class AccessGrantTable(BaseTable):
    resource = tables.LinkColumn(
        'plugins:netbox_azure_groups:protectedresource',
        args=[tables.A('resource.pk')],
        text=lambda record: record.resource.name
    )
    contact = tables.LinkColumn(
        'tenancy:contact',
        args=[tables.A('contact.pk')],
        text=lambda record: record.contact.name
    )
    azure_group = tables.LinkColumn(
        'plugins:netbox_azure_groups:azuregroup',
        args=[tables.A('azure_group.pk')],
        text=lambda record: record.azure_group.name
    )
    control_method = tables.LinkColumn(
        'plugins:netbox_azure_groups:accesscontrolmethod',
        args=[tables.A('control_method.pk')],
        text=lambda record: record.control_method.name
    )
    access_level = ChoiceFieldColumn()
    granted_via = ChoiceFieldColumn()
    is_active = tables.BooleanColumn()
    first_granted = tables.DateTimeColumn(format='M d, Y H:i')
    last_verified = tables.DateTimeColumn(format='M d, Y H:i')

    class Meta(BaseTable.Meta):
        model = AccessGrant
        fields = (
            'resource', 'contact', 'azure_group', 'control_method',
            'access_level', 'granted_via', 'is_active', 
            'first_granted', 'last_verified'
        )
        default_columns = (
            'resource', 'contact', 'azure_group', 'access_level', 
            'granted_via', 'is_active', 'first_granted'
        )