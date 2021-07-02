from django.db import models
from geo.models import Strizh
# Create your models here.
COLOR_CHOICES = (
    ('green','GREEN'),
    ('blue', 'BLUE'),
    ('red','RED'),
    ('orange','ORANGE'),
    ('black','BLACK'),
)

class MyModel(models.Model):
    color = models.CharField(max_length=6, choices=COLOR_CHOICES, default='green')


from django.core.serializers import serialize
import json



class MyStrizh(Strizh):
    geojson_strizhes = serialize('geojson', Strizh.objects.all())
    parsed_json = (json.loads(geojson_strizhes))
    arr_strizh = []
    for i in range(len(parsed_json.get("features"))):
        strizh_name = parsed_json.get("features")[i].get("properties").get("name")
        arr_strizh.append([i, strizh_name])

    choice_strizh = models.CharField(max_length=20, choices=arr_strizh, default='5')

