# Generated manually to create missing GroupOwnership table

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0002_squashed_0059'),
        ('netbox_azure_groups', '0006_enhanced_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupOwnership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('assigned_date', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ownerships',
                    to='netbox_azure_groups.azuregroup'
                )),
                ('contact', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='owned_azure_groups',
                    to='tenancy.contact'
                )),
                ('tags', models.ManyToManyField(blank=True, related_name='%(app_label)s_%(class)s_related', to='extras.tag')),
            ],
            options={
                'verbose_name': 'Group Ownership',
                'verbose_name_plural': 'Group Ownerships',
                'ordering': ['pk'],
            },
        ),
        migrations.AddConstraint(
            model_name='groupownership',
            constraint=models.UniqueConstraint(fields=['group', 'contact'], name='unique_group_contact_ownership'),
        ),
    ]