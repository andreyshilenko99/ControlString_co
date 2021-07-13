import json

from django.contrib.gis.db import models



class Point(models.Model):
    system_name = models.CharField(max_length=50)
    center_freq = models.FloatField()
    brandwidth = models.FloatField()
    detection_time = models.CharField(max_length=50)
    comment_string = models.CharField(max_length=50)
    lat = models.FloatField()
    lon = models.FloatField()
    azimuth = models.CharField(max_length=50)
    area_sector_start_grad = models.FloatField()
    area_sector_end_grad = models.FloatField()
    area_radius_m = models.FloatField()

    def __str__(self):
        return self.system_name

    class Meta:
        verbose_name_plural = 'Дроны'
        verbose_name = 'Дрон'


class Strizh(models.Model):
    name = models.CharField('Имя стрижа', max_length=50, default='стриж 0 (по умолчанию)')
    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Стриж'
        verbose_name_plural = 'Стрижи'


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



