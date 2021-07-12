import json

from django.contrib.gis.db import models


class Point(models.Model):
    name = models.CharField(max_length=50)
    lat = models.FloatField()
    lon = models.FloatField()
    # coordinates = models.
    # mpoint = models.PointField(srid=4328)
    def __str__(self):
        return self.name
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



