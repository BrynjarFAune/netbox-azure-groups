# Generated manually for FortiGate policy model

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_azure_groups', '0009_add_access_control_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='FortiGatePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('policy_id', models.IntegerField(unique=True)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('action', models.CharField(choices=[('accept', 'Accept'), ('deny', 'Deny'), ('ipsec', 'IPSec'), ('ssl-vpn', 'SSL VPN')], max_length=20)),
                ('status', models.CharField(choices=[('enable', 'Enable'), ('disable', 'Disable')], default='enable', max_length=10)),
                ('source_interfaces', models.JSONField(default=list)),
                ('destination_interfaces', models.JSONField(default=list)),
                ('source_addresses', models.JSONField(default=list)),
                ('destination_addresses', models.JSONField(default=list)),
                ('source_address6', models.JSONField(default=list)),
                ('destination_address6', models.JSONField(default=list)),
                ('services', models.JSONField(default=list)),
                ('schedule', models.CharField(blank=True, max_length=100)),
                ('nat_enabled', models.BooleanField(default=False)),
                ('nat_pool', models.CharField(blank=True, max_length=100)),
                ('ip_pool', models.CharField(blank=True, max_length=100)),
                ('utm_status', models.CharField(choices=[('enable', 'Enable'), ('disable', 'Disable')], default='disable', max_length=10)),
                ('av_profile', models.CharField(blank=True, max_length=100)),
                ('webfilter_profile', models.CharField(blank=True, max_length=100)),
                ('dnsfilter_profile', models.CharField(blank=True, max_length=100)),
                ('ips_sensor', models.CharField(blank=True, max_length=100)),
                ('application_list', models.CharField(blank=True, max_length=100)),
                ('ssl_ssh_profile', models.CharField(blank=True, max_length=100)),
                ('log_traffic', models.CharField(choices=[('all', 'All'), ('utm', 'UTM'), ('disable', 'Disable')], default='utm', max_length=20)),
                ('log_traffic_start', models.CharField(choices=[('enable', 'Enable'), ('disable', 'Disable')], default='disable', max_length=10)),
                ('capture_packet', models.CharField(choices=[('enable', 'Enable'), ('disable', 'Disable')], default='disable', max_length=10)),
                ('comments', models.TextField(blank=True)),
                ('ai_description', models.TextField(blank=True, help_text='AI-generated human-readable description of this policy')),
                ('custom_field_data', models.JSONField(blank=True, default=dict, editable=False)),
                ('tags', models.ManyToManyField(blank=True, to='extras.tag')),
            ],
            options={
                'verbose_name': 'FortiGate Policy',
                'verbose_name_plural': 'FortiGate Policies',
                'ordering': ['policy_id'],
            },
        ),
    ]