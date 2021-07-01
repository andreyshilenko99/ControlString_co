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
        verbose_name_plural = 'Incidences'


class Strizh(models.Model):
    name = models.CharField(max_length=50)
    lat = models.FloatField()
    lon = models.FloatField()
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Strizh'

# class LoadDict(models.Model):
#     with open('geo/geojson_file.json', 'r') as reader:
#         x = json.load(reader)
#         print(x)
#
# class Location(models.Model):
#     name = models.CharField(max_length=50)
#     lon = models.FloatField()
#     lat = models.FloatField()
#
#     def serialize(self):
#         json_dict = {}
#         json_dict['type'] = 'Feature'
#         json_dict['properties'] = dict(name=self.name)
#         json_dict['geometry'] = dict(type='Point', coordinates=list([self.lon, self.lat]))
#         return(json.dumps(json_dict))
#
#         # update - allow multiple geoms
#         # return Py dict (will do json.dumps in view)
#         # return (json_dict)
