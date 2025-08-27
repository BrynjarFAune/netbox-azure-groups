import django_tables2 as tables
from netbox.tables import NetBoxTable, ChoiceFieldColumn
from .models import AzureGroup, GroupMembership


class AzureGroupTable(NetBoxTable):
    name = tables.Column(linkify=True)
    group_type = ChoiceFieldColumn()
    member_count = tables.Column(
        verbose_name='Members',
        accessor='member_count',
        orderable=False
    )
    is_security_enabled = tables.BooleanColumn(verbose_name='Security')
    is_mail_enabled = tables.BooleanColumn(verbose_name='Mail')

    class Meta(NetBoxTable.Meta):
        model = AzureGroup
        fields = (
            'pk', 'id', 'name', 'description', 'object_id', 'mail',
            'group_type', 'is_security_enabled', 'is_mail_enabled',
            'member_count', 'created_datetime', 'created', 'last_updated',
            'actions'
        )
        default_columns = (
            'pk', 'name', 'group_type', 'member_count',
            'is_security_enabled', 'is_mail_enabled'
        )


class GroupMembershipTable(NetBoxTable):
    group = tables.Column(linkify=True)
    member = tables.Column(
        accessor='member',
        verbose_name='Member',
        orderable=False
    )
    content_type = tables.Column(verbose_name='Type')
    member_type = ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = GroupMembership
        fields = (
            'pk', 'id', 'group', 'member', 'content_type',
            'member_type', 'created', 'last_updated', 'actions'
        )
        default_columns = ('pk', 'group', 'member', 'content_type', 'member_type')