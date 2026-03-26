# Generated manually on 2026-03-25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_company_export_info_infringementoverview'),
    ]

    operations = [
        migrations.RenameField(
            model_name='infringementoverview',
            old_name='event_to_quote',
            new_name='event_to_quotes',
        ),
        migrations.AlterField(
            model_name='infringementoverview',
            name='event_to_quotes',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='infringementoverview',
            name='infringement_address',
            field=models.TextField(blank=True),
        ),
    ]
