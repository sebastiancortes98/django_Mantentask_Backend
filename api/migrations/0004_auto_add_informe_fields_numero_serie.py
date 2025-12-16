from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_merge_0002_solicitud_fecha_programada_0002_usuario_telefono'),
    ]

    operations = [
        migrations.AddField(
            model_name='informe',
            name='descripcion_trabajo',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='informe',
            name='piezas_reemplazadas',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='informe',
            name='recomendaciones',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='maquina',
            name='numero_serie',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
