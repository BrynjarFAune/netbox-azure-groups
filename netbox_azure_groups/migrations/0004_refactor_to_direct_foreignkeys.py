# Migration to refactor from GenericForeignKey to direct ForeignKey relationships

from django.db import migrations, models
import django.db.models.deletion


def migrate_data_forward(apps, schema_editor):
    """Convert existing GenericForeignKey data to direct ForeignKey relationships"""
    # Get model classes for the migration
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Old models
    GroupOwnership = apps.get_model('netbox_azure_groups', 'GroupOwnership')
    GroupMembership = apps.get_model('netbox_azure_groups', 'GroupMembership')
    
    # New models  
    ContactGroupOwnership = apps.get_model('netbox_azure_groups', 'ContactGroupOwnership')
    ContactGroupMembership = apps.get_model('netbox_azure_groups', 'ContactGroupMembership')
    DeviceGroupMembership = apps.get_model('netbox_azure_groups', 'DeviceGroupMembership')
    
    # Get ContentType instances
    try:
        contact_ct = ContentType.objects.get(app_label='tenancy', model='contact')
        device_ct = ContentType.objects.get(app_label='dcim', model='device')
    except ContentType.DoesNotExist:
        print("ContentType not found, skipping data migration")
        return
    
    # Migrate GroupOwnership data (only contacts can own groups)
    for ownership in GroupOwnership.objects.all():
        if ownership.content_type == contact_ct:
            ContactGroupOwnership.objects.create(
                group=ownership.group,
                contact_id=ownership.object_id
            )
            print(f"Migrated ownership: {ownership.group.name} -> Contact {ownership.object_id}")
    
    # Migrate GroupMembership data
    for membership in GroupMembership.objects.all():
        if membership.content_type == contact_ct:
            ContactGroupMembership.objects.create(
                group=membership.group,
                contact_id=membership.object_id,
                member_type=membership.member_type
            )
            print(f"Migrated contact membership: {membership.group.name} -> Contact {membership.object_id}")
        elif membership.content_type == device_ct:
            DeviceGroupMembership.objects.create(
                group=membership.group,
                device_id=membership.object_id,
                member_type=membership.member_type
            )
            print(f"Migrated device membership: {membership.group.name} -> Device {membership.object_id}")


def migrate_data_reverse(apps, schema_editor):
    """Convert direct ForeignKey relationships back to GenericForeignKey data"""
    # This is complex and not implemented for now
    # In practice, you'd rarely reverse this migration
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('tenancy', '0001_initial'),
        ('dcim', '0001_initial'),
        ('netbox_azure_groups', '0003_suppress_auto_display'),
    ]

    operations = [
        # Create new direct ForeignKey models
        migrations.CreateModel(
            name='ContactGroupOwnership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='azure_group_ownerships', to='tenancy.contact')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contact_ownerships', to='netbox_azure_groups.azuregroup')),
            ],
            options={
                'verbose_name': 'Contact Group Ownership',
                'verbose_name_plural': 'Contact Group Ownerships',
                'ordering': ['group__name'],
            },
        ),
        migrations.CreateModel(
            name='ContactGroupMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('member_type', models.CharField(choices=[('direct', 'Direct Member'), ('nested', 'Nested Member')], default='direct', help_text='Type of group membership', max_length=20)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='azure_group_memberships', to='tenancy.contact')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contact_memberships', to='netbox_azure_groups.azuregroup')),
            ],
            options={
                'verbose_name': 'Contact Group Membership',
                'verbose_name_plural': 'Contact Group Memberships',
                'ordering': ['group__name'],
            },
        ),
        migrations.CreateModel(
            name='DeviceGroupMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('member_type', models.CharField(choices=[('direct', 'Direct Member'), ('nested', 'Nested Member')], default='direct', help_text='Type of group membership', max_length=20)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='azure_group_memberships', to='dcim.device')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='device_memberships', to='netbox_azure_groups.azuregroup')),
            ],
            options={
                'verbose_name': 'Device Group Membership', 
                'verbose_name_plural': 'Device Group Memberships',
                'ordering': ['group__name'],
            },
        ),
        
        # Add unique constraints
        migrations.AlterUniqueTogether(
            name='contactgroupownership',
            unique_together={('group', 'contact')},
        ),
        migrations.AlterUniqueTogether(
            name='contactgroupmembership',
            unique_together={('group', 'contact')},
        ),
        migrations.AlterUniqueTogether(
            name='devicegroupmembership',
            unique_together={('group', 'device')},
        ),
        
        # Migrate existing data
        migrations.RunPython(migrate_data_forward, migrate_data_reverse),
        
        # Remove old GenericForeignKey models
        migrations.DeleteModel(name='GroupOwnership'),
        migrations.DeleteModel(name='GroupMembership'),
    ]