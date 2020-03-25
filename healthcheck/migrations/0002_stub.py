from django.db import migrations


class Migration(migrations.Migration):

    def initial_entry(apps, schema_editor):
        HealthCheck = apps.get_model('healthcheck', 'HealthCheck')
        HealthCheck.objects.create(health_check_field=True)

    dependencies = [
        ('healthcheck', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_entry),
    ]
