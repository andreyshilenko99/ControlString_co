# Generated by Django 3.2.4 on 2021-08-09 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0002_apemsconfiguration_strizh_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apemsconfiguration',
            name='strizh_name',
            field=models.CharField(choices=[(1, 'стриж 1. АСБ'), (2, 'стриж 2 (СКЛАД)')], max_length=500, verbose_name='Имя стрижа'),
        ),
    ]
