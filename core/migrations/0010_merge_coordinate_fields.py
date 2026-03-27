from django.db import migrations, models


def _merge_pair(first, second):
    first = (first or '').strip()
    second = (second or '').strip()
    if first and second:
        return f"{first}, {second}"
    return first or second


def forwards(apps, schema_editor):
    InfringementDetail = apps.get_model('core', 'InfringementDetail')

    for detail in InfringementDetail.objects.all():
        detail.wifi_latitude_longitude = _merge_pair(detail.wifi_latitude, detail.wifi_longitude)
        detail.ip_latitude_longitude = _merge_pair(detail.ip_latitude, detail.ip_longitude)
        detail.save(update_fields=['wifi_latitude_longitude', 'ip_latitude_longitude'])


def backwards(apps, schema_editor):
    InfringementDetail = apps.get_model('core', 'InfringementDetail')

    for detail in InfringementDetail.objects.all():
        wifi_pair = (detail.wifi_latitude_longitude or '').split(',', 1)
        ip_pair = (detail.ip_latitude_longitude or '').split(',', 1)

        detail.wifi_latitude = wifi_pair[0].strip() if wifi_pair else ''
        detail.wifi_longitude = wifi_pair[1].strip() if len(wifi_pair) > 1 else ''
        detail.ip_latitude = ip_pair[0].strip() if ip_pair else ''
        detail.ip_longitude = ip_pair[1].strip() if len(ip_pair) > 1 else ''
        detail.save(update_fields=['wifi_latitude', 'wifi_longitude', 'ip_latitude', 'ip_longitude'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_update_infringement_detail_company_mapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='infringementdetail',
            name='wifi_latitude_longitude',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='infringementdetail',
            name='ip_latitude_longitude',
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(
            model_name='infringementdetail',
            name='wifi_latitude',
        ),
        migrations.RemoveField(
            model_name='infringementdetail',
            name='wifi_longitude',
        ),
        migrations.RemoveField(
            model_name='infringementdetail',
            name='ip_latitude',
        ),
        migrations.RemoveField(
            model_name='infringementdetail',
            name='ip_longitude',
        ),
    ]
