# Generated for NetBox Azure Groups Plugin

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0020_remove_contactgroupmembership'),
        ('dcim', '0210_macaddress_ordering'),
        ('netbox_azure_groups', '0005_contactgroupmembership_custom_field_data_and_more'),
    ]

    operations = [
        # Add new fields to AzureGroup to replace the old ones
        migrations.AddField(
            model_name='azuregroup',
            name='azure_created',
            field=models.DateTimeField(blank=True, help_text='When the group was created in Azure AD', null=True),
        ),
        migrations.AddField(
            model_name='azuregroup',
            name='azure_modified',
            field=models.DateTimeField(blank=True, help_text='When the group was last modified in Azure AD', null=True),
        ),
        migrations.AddField(
            model_name='azuregroup',
            name='group_type',
            field=models.CharField(
                choices=[
                    ('security', 'Security Group'), 
                    ('microsoft365', 'Microsoft 365 Group'), 
                    ('mail_security', 'Mail-Enabled Security'), 
                    ('distribution', 'Distribution List'), 
                    ('dynamic_security', 'Dynamic Security'), 
                    ('dynamic_m365', 'Dynamic Microsoft 365')
                ], 
                db_index=True, 
                default='security', 
                help_text='Type of Azure AD group', 
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='azuregroup',
            name='source',
            field=models.CharField(
                choices=[
                    ('azure_ad', 'Azure AD Native'), 
                    ('on_premises', 'On-Premises AD'), 
                    ('external', 'External Directory')
                ], 
                db_index=True, 
                default='azure_ad', 
                help_text='Where group is mastered', 
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='azuregroup',
            name='is_security_enabled',
            field=models.BooleanField(default=False, help_text='Whether the group is security-enabled'),
        ),
        migrations.AddField(
            model_name='azuregroup',
            name='is_mail_enabled',
            field=models.BooleanField(default=False, help_text='Whether the group is mail-enabled'),
        ),
        migrations.AddField(
            model_name='azuregroup',
            name='mail',
            field=models.EmailField(blank=True, db_index=True, help_text='Group email address', max_length=254),
        ),
        migrations.AddField(
            model_name='azuregroup',
            name='membership_type',
            field=models.CharField(
                choices=[('assigned', 'Assigned'), ('dynamic', 'Dynamic')], 
                default='assigned', 
                help_text='Type of membership assignment', 
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='azuregroup',
            name='membership_rule',
            field=models.TextField(blank=True, help_text='Azure AD dynamic membership rule'),
        ),
        migrations.AddField(
            model_name='azuregroup',
            name='member_count',
            field=models.IntegerField(default=0, help_text='Total number of members'),
        ),
        migrations.AddField(
            model_name='azuregroup',
            name='owner_count',
            field=models.IntegerField(default=0, help_text='Total number of owners'),
        ),
        migrations.AddField(
            model_name='azuregroup',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Soft delete flag for audit retention'),
        ),

        # Create new GroupMembership model
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('tags', models.ManyToManyField(blank=True, to='extras.tag')),
                ('membership_type', models.CharField(
                    choices=[('direct', 'Direct Member'), ('nested', 'Via Nested Group'), ('dynamic', 'Dynamic Rule Match')], 
                    default='direct', 
                    max_length=20
                )),
                ('nested_via', models.JSONField(blank=True, help_text='Group IDs traversed for nested membership', null=True)),
                ('contact', models.ForeignKey(
                    blank=True, 
                    null=True, 
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='azure_group_memberships', 
                    to='tenancy.contact'
                )),
                ('device', models.ForeignKey(
                    blank=True, 
                    null=True, 
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='azure_group_memberships', 
                    to='dcim.device'
                )),
                ('group', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='memberships', 
                    to='netbox_azure_groups.azuregroup'
                )),
            ],
            options={
                'verbose_name': 'Group Membership',
                'verbose_name_plural': 'Group Memberships',
                'ordering': ['pk'],
                'indexes': [
                    models.Index(fields=['group', 'membership_type'], name='netbox_azure_groups_groupmembership_group_type_idx')
                ],
            },
        ),

        # Create ProtectedResource model
        migrations.CreateModel(
            name='ProtectedResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('tags', models.ManyToManyField(blank=True, to='extras.tag')),
                ('name', models.CharField(
                    help_text='Resource name (e.g., "HR Database", "Server Room A", "Finance Portal")', 
                    max_length=200, 
                    unique=True
                )),
                ('resource_type', models.CharField(
                    choices=[
                        ('web_application', 'Web Application'), 
                        ('database', 'Database'), 
                        ('api_service', 'API Service'), 
                        ('file_share', 'File Share'), 
                        ('physical_location', 'Physical Location'), 
                        ('network_device', 'Network Device'), 
                        ('cloud_resource', 'Cloud Resource'), 
                        ('other', 'Other')
                    ], 
                    help_text='Type of protected resource', 
                    max_length=50
                )),
                ('description', models.TextField(blank=True, help_text='Resource description and purpose')),
                ('base_url', models.URLField(blank=True, help_text='Resource URL if applicable')),
                ('ip_addresses', models.JSONField(blank=True, default=list, help_text='IP addresses associated with this resource')),
                ('physical_location', models.CharField(blank=True, help_text='Physical location (e.g., "Building A, Room 101")', max_length=200)),
                ('business_unit', models.CharField(blank=True, help_text='Business unit that owns this resource', max_length=100)),
                ('criticality', models.CharField(
                    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], 
                    default='medium', 
                    help_text='Business criticality of this resource', 
                    max_length=20
                )),
                ('is_active', models.BooleanField(default=True, help_text='Whether resource is currently active')),
                ('owner_contact', models.ForeignKey(
                    blank=True, 
                    help_text='Contact responsible for this resource', 
                    null=True, 
                    on_delete=django.db.models.deletion.SET_NULL, 
                    related_name='owned_resources', 
                    to='tenancy.contact'
                )),
            ],
            options={
                'verbose_name': 'Protected Resource',
                'verbose_name_plural': 'Protected Resources',
                'ordering': ['name'],
                'indexes': [
                    models.Index(fields=['resource_type', 'is_active'], name='netbox_azure_groups_protectedresource_type_active_idx'),
                    models.Index(fields=['criticality'], name='netbox_azure_groups_protectedresource_criticality_idx'),
                    models.Index(fields=['owner_contact'], name='netbox_azure_groups_protectedresource_owner_idx'),
                ],
            },
        ),

        # Create AccessControlMethod model
        migrations.CreateModel(
            name='AccessControlMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('tags', models.ManyToManyField(blank=True, to='extras.tag')),
                ('control_type', models.CharField(
                    choices=[
                        ('fortigate_policy', 'FortiGate Firewall Policy'), 
                        ('badge_reader', 'Physical Badge Reader'), 
                        ('vpn_config', 'VPN Configuration'), 
                        ('application_rbac', 'Application Role'), 
                        ('network_acl', 'Network ACL'), 
                        ('cloud_iam', 'Cloud IAM Policy'), 
                        ('manual_process', 'Manual Process'), 
                        ('other', 'Other')
                    ], 
                    help_text='Type of access control mechanism', 
                    max_length=50
                )),
                ('name', models.CharField(help_text='Control mechanism name (e.g., "Policy-42", "Door-Controller-A")', max_length=200)),
                ('description', models.TextField(blank=True, help_text='How this control method works')),
                ('access_level', models.CharField(
                    choices=[
                        ('read', 'Read Only'), 
                        ('write', 'Read/Write'), 
                        ('admin', 'Administrative'), 
                        ('full', 'Full Access'), 
                        ('physical', 'Physical Access')
                    ], 
                    default='read', 
                    help_text='Level of access granted', 
                    max_length=20
                )),
                ('configuration', models.JSONField(blank=True, default=dict, help_text='Type-specific configuration details')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this control method is currently active')),
                ('last_verified', models.DateTimeField(blank=True, help_text='When this configuration was last verified', null=True)),
                ('azure_group', models.ForeignKey(
                    help_text='Azure group that provides access through this method', 
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='enables_access_via', 
                    to='netbox_azure_groups.azuregroup'
                )),
                ('resource', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='access_methods', 
                    to='netbox_azure_groups.protectedresource'
                )),
            ],
            options={
                'verbose_name': 'Access Control Method',
                'verbose_name_plural': 'Access Control Methods',
                'ordering': ['resource', 'name'],
                'indexes': [
                    models.Index(fields=['resource', 'is_active'], name='netbox_azure_groups_accesscontrolmethod_resource_active_idx'),
                    models.Index(fields=['control_type'], name='netbox_azure_groups_accesscontrolmethod_control_type_idx'),
                    models.Index(fields=['azure_group'], name='netbox_azure_groups_accesscontrolmethod_azure_group_idx'),
                ],
            },
        ),

        # Create AccessGrant model  
        migrations.CreateModel(
            name='AccessGrant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('tags', models.ManyToManyField(blank=True, to='extras.tag')),
                ('access_level', models.CharField(
                    choices=[
                        ('read', 'Read Only'), 
                        ('write', 'Read/Write'), 
                        ('admin', 'Administrative'), 
                        ('full', 'Full Access'), 
                        ('physical', 'Physical Access')
                    ], 
                    help_text='Level of access granted (inherited from control method)', 
                    max_length=20
                )),
                ('granted_via', models.CharField(
                    choices=[
                        ('direct_membership', 'Direct Group Membership'), 
                        ('nested_membership', 'Nested Group Membership'), 
                        ('inherited', 'Inherited Permission')
                    ], 
                    default='direct_membership', 
                    help_text='How the access was granted', 
                    max_length=30
                )),
                ('first_granted', models.DateTimeField(auto_now_add=True, help_text='When access was first granted')),
                ('last_verified', models.DateTimeField(auto_now=True, help_text='When access was last verified')),
                ('is_active', models.BooleanField(default=True, help_text='Whether access is currently active')),
                ('azure_group', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='access_grants', 
                    to='netbox_azure_groups.azuregroup'
                )),
                ('contact', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='access_grants', 
                    to='tenancy.contact'
                )),
                ('control_method', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='access_grants', 
                    to='netbox_azure_groups.accesscontrolmethod'
                )),
                ('resource', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, 
                    related_name='access_grants', 
                    to='netbox_azure_groups.protectedresource'
                )),
            ],
            options={
                'verbose_name': 'Access Grant',
                'verbose_name_plural': 'Access Grants',
                'ordering': ['-first_granted'],
                'indexes': [
                    models.Index(fields=['resource', 'is_active'], name='netbox_azure_groups_accessgrant_resource_active_idx'),
                    models.Index(fields=['contact', 'is_active'], name='netbox_azure_groups_accessgrant_contact_active_idx'),
                    models.Index(fields=['azure_group'], name='netbox_azure_groups_accessgrant_azure_group_idx'),
                    models.Index(fields=['first_granted'], name='netbox_azure_groups_accessgrant_first_granted_idx'),
                ],
            },
        ),

        # Add unique constraints
        migrations.AddConstraint(
            model_name='groupmembership',
            constraint=models.UniqueConstraint(fields=('group', 'contact'), name='unique_group_contact_membership'),
        ),
        migrations.AddConstraint(
            model_name='groupmembership',
            constraint=models.UniqueConstraint(fields=('group', 'device'), name='unique_group_device_membership'),
        ),
        migrations.AddConstraint(
            model_name='accesscontrolmethod',
            constraint=models.UniqueConstraint(fields=('resource', 'name'), name='unique_resource_control_method'),
        ),
        migrations.AddConstraint(
            model_name='accessgrant',
            constraint=models.UniqueConstraint(
                fields=('resource', 'contact', 'azure_group', 'control_method'), 
                name='unique_access_grant'
            ),
        ),

        # Add new indexes to AzureGroup
        migrations.AddIndex(
            model_name='azuregroup',
            index=models.Index(fields=['source', 'group_type'], name='netbox_azure_groups_azuregroup_source_type_idx'),
        ),
        migrations.AddIndex(
            model_name='azuregroup',
            index=models.Index(fields=['last_sync'], name='netbox_azure_groups_azuregroup_last_sync_idx'),
        ),
    ]