import django_tables2 as tables
from netbox.tables import BaseTable, ChoiceFieldColumn
from .models import AzureGroup


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