import django_tables2 as tables
from netbox.tables import NetBoxTable, ChoiceFieldColumn
from .models import AzureGroup, ContactGroupMembership, ContactGroupOwnership, DeviceGroupMembership


class AzureGroupTable(NetBoxTable):
    name = tables.Column(linkify=True)
    group_type = ChoiceFieldColumn()
    total_member_count = tables.Column(
        verbose_name='Members',
        accessor='total_member_count',
        orderable=False
    )
    is_security_enabled = tables.BooleanColumn(verbose_name='Security')
    is_mail_enabled = tables.BooleanColumn(verbose_name='Mail')

    class Meta(NetBoxTable.Meta):
        model = AzureGroup
        fields = (
            'pk', 'id', 'name', 'description', 'object_id', 'mail',
            'group_type', 'is_security_enabled', 'is_mail_enabled',
            'total_member_count', 'created_datetime', 'created', 'last_updated',
            'actions'
        )
        default_columns = (
            'pk', 'name', 'group_type', 'total_member_count',
            'is_security_enabled', 'is_mail_enabled'
        )


class ContactGroupMembershipTable(NetBoxTable):
    group = tables.Column(linkify=True)
    contact = tables.Column(linkify=True)
    member_type = ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = ContactGroupMembership
        fields = (
            'pk', 'id', 'group', 'contact', 'member_type', 
            'created', 'last_updated', 'actions'
        )
        default_columns = ('pk', 'group', 'contact', 'member_type')


class DeviceGroupMembershipTable(NetBoxTable):
    group = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    member_type = ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = DeviceGroupMembership
        fields = (
            'pk', 'id', 'group', 'device', 'member_type',
            'created', 'last_updated', 'actions'
        )
        default_columns = ('pk', 'group', 'device', 'member_type')


class ContactGroupOwnershipTable(NetBoxTable):
    group = tables.Column(linkify=True)
    contact = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = ContactGroupOwnership
        fields = (
            'pk', 'id', 'group', 'contact',
            'created', 'last_updated', 'actions'
        )
        default_columns = ('pk', 'group', 'contact')