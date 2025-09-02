# Complete FortiGate policy model migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0001_initial'),
        ('tenancy', '0001_initial'),
        ('netbox_azure_groups', '0009_add_access_control_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='FortiGatePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, editable=False)),
                ('policy_id', models.IntegerField(help_text='FortiGate policy ID number', unique=True)),
                ('name', models.CharField(blank=True, help_text='Policy name/description', max_length=200)),
                ('uuid', models.CharField(blank=True, help_text='FortiGate policy UUID', max_length=36)),
                ('status', models.CharField(choices=[('enable', 'Enabled'), ('disable', 'Disabled')], default='enable', help_text='Policy status (enabled/disabled)', max_length=10)),
                ('action', models.CharField(choices=[('accept', 'Accept/Allow'), ('deny', 'Deny/Block'), ('ipsec', 'IPSec')], default='accept', help_text='Policy action (accept/deny/ipsec)', max_length=10)),
                ('source_interfaces', models.JSONField(blank=True, default=list, help_text='Source interfaces (e.g., ["lan", "dmz"])')),
                ('destination_interfaces', models.JSONField(blank=True, default=list, help_text='Destination interfaces (e.g., ["wan1", "wan2"])')),
                ('source_addresses', models.JSONField(blank=True, default=list, help_text='Source address objects (e.g., ["all", "internal_network"])')),
                ('destination_addresses', models.JSONField(blank=True, default=list, help_text='Destination address objects (e.g., ["all", "web_servers"])')),
                ('services', models.JSONField(blank=True, default=list, help_text='Service objects (e.g., ["ALL", "HTTP", "HTTPS"])')),
                ('nat_enabled', models.BooleanField(default=False, help_text='Whether NAT is enabled for this policy')),
                ('nat_type', models.CharField(blank=True, choices=[('snat', 'Source NAT'), ('dnat', 'Destination NAT'), ('both', 'Both SNAT and DNAT')], help_text='Type of NAT applied', max_length=20)),
                ('nat_outbound_interface', models.CharField(blank=True, help_text='Outbound interface for NAT', max_length=50)),
                ('nat_pool_name', models.CharField(blank=True, help_text='NAT pool name if using IP pool', max_length=100)),
                ('utm_status', models.CharField(choices=[('enable', 'Enabled'), ('disable', 'Disabled')], default='disable', help_text='UTM (security profiles) status', max_length=10)),
                ('profile_group', models.CharField(blank=True, help_text='Security profile group name', max_length=100)),
                ('log_traffic', models.CharField(choices=[('all', 'All'), ('utm', 'UTM'), ('disable', 'Disabled')], default='utm', help_text='Traffic logging setting', max_length=10)),
                ('schedule', models.CharField(default='always', help_text='Schedule name (default: always)', max_length=100)),
                ('groups', models.JSONField(blank=True, default=list, help_text='User groups for authentication')),
                ('comments', models.TextField(blank=True, help_text='FortiGate policy comments/notes')),
                ('ai_description', models.TextField(blank=True, help_text='AI-generated description of what this policy does')),
                ('fortigate_host', models.CharField(help_text='FortiGate hostname/IP this policy came from', max_length=100)),
                ('vdom', models.CharField(default='root', help_text='FortiGate VDOM', max_length=50)),
                ('last_fetched', models.DateTimeField(auto_now=True, help_text='When this policy was last fetched from FortiGate')),
                ('access_control_method', models.ForeignKey(blank=True, help_text='Associated access control method if this policy provides resource access', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fortigate_policies', to='netbox_azure_groups.accesscontrolmethod')),
                ('tags', models.ManyToManyField(blank=True, to='extras.tag')),
            ],
            options={
                'verbose_name': 'FortiGate Policy',
                'verbose_name_plural': 'FortiGate Policies',
                'ordering': ['policy_id'],
                'indexes': [
                    models.Index(fields=['policy_id'], name='netbox_azur_policy__ab7ca5_idx'),
                    models.Index(fields=['action', 'status'], name='netbox_azur_action_69e8c9_idx'),
                    models.Index(fields=['fortigate_host', 'vdom'], name='netbox_azur_fortiga_e2c8f1_idx'),
                    models.Index(fields=['last_fetched'], name='netbox_azur_last_fe_7b8a1c_idx'),
                ],
            },
        ),
        migrations.AlterUniqueTogether(
            name='fortigatepolicy',
            unique_together={('fortigate_host', 'vdom', 'policy_id')},
        ),
    ]