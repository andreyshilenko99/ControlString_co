from django.contrib.gis.db import models
from django.db.models import Manager as GeoManager


class Point(models.Model):
    name = models.CharField(max_length=50)
    lat = models.FloatField()
    lon = models.FloatField()
    mpoint = models.PointField(srid=4326)
    objects = GeoManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Incidences'
