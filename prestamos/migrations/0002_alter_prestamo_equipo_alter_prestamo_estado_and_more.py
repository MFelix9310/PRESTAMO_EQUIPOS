# Generated by Django 5.2.1 on 2025-05-19 17:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prestamos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prestamo',
            name='equipo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prestamos_antiguos', to='prestamos.equipo', verbose_name='Equipo (Deprecado)'),
        ),
        migrations.AlterField(
            model_name='prestamo',
            name='estado',
            field=models.CharField(choices=[('PRESTADO', 'Prestado'), ('DEVUELTO', 'Devuelto'), ('DEVUELTO_PARCIAL', 'Devuelto Parcialmente'), ('RETRASADO', 'Retrasado')], default='PRESTADO', max_length=20, verbose_name='Estado'),
        ),
        migrations.CreateModel(
            name='DetallePrestamo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_devolucion_real', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Devolución Real')),
                ('estado', models.CharField(choices=[('PRESTADO', 'Prestado'), ('DEVUELTO', 'Devuelto'), ('RETRASADO', 'Retrasado')], default='PRESTADO', max_length=10, verbose_name='Estado')),
                ('observaciones', models.TextField(blank=True, null=True, verbose_name='Observaciones')),
                ('equipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles_prestamo', to='prestamos.equipo', verbose_name='Equipo')),
                ('prestamo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='prestamos.prestamo', verbose_name='Préstamo')),
            ],
            options={
                'verbose_name': 'Detalle de Préstamo',
                'verbose_name_plural': 'Detalles de Préstamo',
                'ordering': ['-prestamo__fecha_prestamo'],
                'unique_together': {('prestamo', 'equipo')},
            },
        ),
    ]
