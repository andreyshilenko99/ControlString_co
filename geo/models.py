import json

from django.contrib.gis.db import models



class Point(models.Model):
    system_name = models.CharField('Имя дрона', max_length=50)
    center_freq = models.FloatField('Несущая частота')
    brandwidth = models.FloatField('Пропускная способность')
    detection_time = models.CharField('Время обнаружения', max_length=50)
    comment_string = models.CharField('Комментарии', max_length=50)
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    azimuth = models.CharField('Азимут', max_length=50)
    area_sector_start_grad = models.FloatField('Внутренний радиус сектора')
    area_sector_end_grad = models.FloatField('Внешний радиус сектора')
    area_radius_m = models.FloatField('Радиус сектора (м)')
    ip = models.CharField('IP-адрес стрижа', max_length=50)

    def __str__(self):
        return self.system_name

    class Meta:
        verbose_name_plural = 'Дроны'
        verbose_name = 'Дрон'


class Strizh(models.Model):
    name = models.CharField('Имя стрижа', max_length=50, default='стриж 0 (по умолчанию)')
    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)
    ip = models.CharField('IP-адрес стрижа', max_length=50, default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Стриж'
        verbose_name_plural = 'Стрижи'
        ordering = ['name']


class Sector(models.Model):
    name = models.CharField(max_length=50)
    center_lat = models.FloatField()
    center_lon = models.FloatField()
    innerRadius = models.FloatField(default=0)
    outerRadius = models.FloatField(default=500)
    startBearing = models.FloatField()
    endBearing = models.FloatField()
    color = models.CharField(max_length=50, default='yellow')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Sector'



