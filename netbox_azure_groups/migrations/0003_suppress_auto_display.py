# Generated manually to suppress NetBox auto-display of reverse relationships

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('netbox_azure_groups', '0002_groupownership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupownership',
            name='content_type',
            field=models.ForeignKey(
                limit_choices_to=models.Q(app_label='tenancy', model='contact'),
                on_delete=django.db.models.deletion.CASCADE,
                related_name='+',
                to='contenttypes.contenttype'
            ),
        ),
        migrations.AlterField(
            model_name='groupmembership',
            name='content_type',
            field=models.ForeignKey(
                limit_choices_to=models.Q(
                    models.Q(('app_label', 'tenancy'), ('model', 'contact')) |
                    models.Q(('app_label', 'dcim'), ('model', 'device'))
                ),
                on_delete=django.db.models.deletion.CASCADE,
                related_name='+',
                to='contenttypes.contenttype'
            ),
        ),
    ]