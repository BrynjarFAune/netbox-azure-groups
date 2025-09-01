# Generated manually to fix related_name attributes

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_azure_groups', '0006_enhanced_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupownership',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_azure_groups', to='tenancy.contact'),
        ),
    ]