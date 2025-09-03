# Generated manually for netbox_azure_groups

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0001_initial'),
        ('tenancy', '0001_initial'),
        ('netbox_azure_groups', '0009_add_access_control_models'),
    ]

    operations = [
        # Create BusinessUnit model
        migrations.CreateModel(
            name='BusinessUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('name', models.CharField(help_text='Business unit name (e.g., "Human Resources", "Finance", "IT")', max_length=100, unique=True)),
                ('description', models.TextField(blank=True, help_text='Business unit description and purpose')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this business unit is active')),
                ('contact', models.ForeignKey(blank=True, help_text='Business unit manager/contact', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_business_units', to='tenancy.contact')),
                ('parent', models.ForeignKey(blank=True, help_text='Parent business unit (for hierarchical structure)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='netbox_azure_groups.businessunit')),
            ],
            options={
                'verbose_name': 'Business Unit',
                'verbose_name_plural': 'Business Units',
                'ordering': ['name'],
            },
        ),
        # Add site field to ProtectedResource
        migrations.AddField(
            model_name='protectedresource',
            name='site',
            field=models.ForeignKey(blank=True, help_text='NetBox site where this resource is located', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='protected_resources', to='dcim.site'),
        ),
        # Add location field to ProtectedResource
        migrations.AddField(
            model_name='protectedresource',
            name='location',
            field=models.ForeignKey(blank=True, help_text='Specific location within the site', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='protected_resources', to='dcim.location'),
        ),
        # Remove old business_unit CharField (if it exists)
        migrations.RemoveField(
            model_name='protectedresource',
            name='business_unit',
        ),
        # Add new business_unit ForeignKey field
        migrations.AddField(
            model_name='protectedresource',
            name='business_unit',
            field=models.ForeignKey(blank=True, help_text='Business unit that owns this resource', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resources', to='netbox_azure_groups.businessunit'),
        ),
    ]