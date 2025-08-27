# Generated Django migration for NetBox Azure Groups plugin

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0002_squashed_0059'),
    ]

    operations = [
        migrations.CreateModel(
            name='AzureGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('name', models.CharField(help_text='Group display name', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Group description')),
                ('object_id', models.CharField(help_text='Azure AD Object ID (GUID)', max_length=36, unique=True)),
                ('mail', models.EmailField(blank=True, help_text='Group email address', max_length=254)),
                ('group_type', models.CharField(choices=[('security', 'Security'), ('distribution', 'Distribution'), ('microsoft365', 'Microsoft 365')], default='security', help_text='Type of Azure AD group', max_length=20)),
                ('is_security_enabled', models.BooleanField(default=True, help_text='Whether the group is security-enabled')),
                ('is_mail_enabled', models.BooleanField(default=False, help_text='Whether the group is mail-enabled')),
                ('created_datetime', models.DateTimeField(blank=True, help_text='When the group was created in Azure AD', null=True)),
                ('tags', models.ManyToManyField(blank=True, related_name='%(app_label)s_%(class)s_related', to='extras.tag')),
            ],
            options={
                'verbose_name': 'Azure Group',
                'verbose_name_plural': 'Azure Groups',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('object_id', models.PositiveIntegerField()),
                ('member_type', models.CharField(choices=[('direct', 'Direct Member'), ('nested', 'Nested Member')], default='direct', help_text='Type of group membership', max_length=20)),
                ('content_type', models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'tenancy'), ('model', 'contact')), models.Q(('app_label', 'dcim'), ('model', 'device')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='netbox_azure_groups.azuregroup')),
                ('tags', models.ManyToManyField(blank=True, related_name='%(app_label)s_%(class)s_related', to='extras.tag')),
            ],
            options={
                'verbose_name': 'Group Membership',
                'verbose_name_plural': 'Group Memberships',
                'ordering': ['group__name'],
            },
        ),
        migrations.AddConstraint(
            model_name='groupmembership',
            constraint=models.UniqueConstraint(fields=('group', 'content_type', 'object_id'), name='unique_group_membership'),
        ),
    ]