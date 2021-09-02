# Generated by Django 3.2.4 on 2021-08-11 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0004_alter_apemsconfiguration_strizh_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apemsconfiguration',
            name='strizh_name',
            field=models.CharField(choices=[('стриж 1. АСБ', 'стриж 1. АСБ')], error_messages={'required': ''}, max_length=500, verbose_name='Имя стрижа'),
        ),
    ]