from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud',
            name='fecha_programada',
            field=models.DateField(null=True, blank=True),
        ),
    ]
