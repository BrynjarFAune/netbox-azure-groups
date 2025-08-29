import django_tables2 as tables
from netbox.tables import NetBoxTable, ChoiceFieldColumn
from .models import AzureGroup


class AzureGroupTable(NetBoxTable):
    name = tables.Column(linkify=True)
    source = ChoiceFieldColumn()
    group_type = ChoiceFieldColumn()
    membership_type = ChoiceFieldColumn()
    member_count = tables.Column(
        verbose_name='Members',
        orderable=True
    )
    is_security_enabled = tables.BooleanColumn(verbose_name='Security')
    is_mail_enabled = tables.BooleanColumn(verbose_name='Mail')

    class Meta(NetBoxTable.Meta):
        model = AzureGroup
        fields = (
            'pk', 'id', 'name', 'description', 'object_id', 'mail',
            'source', 'group_type', 'membership_type', 
            'is_security_enabled', 'is_mail_enabled',
            'member_count', 'azure_created', 'created', 'last_updated',
            'actions'
        )
        default_columns = (
            'pk', 'name', 'source', 'group_type', 'member_count',
            'is_security_enabled', 'is_mail_enabled'
        )