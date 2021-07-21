from django.db import models

from geo.models import Strizh

from django.core.serializers import serialize
import json
# Create your models here.
COLOR_CHOICES = (
    ('green', 'GREEN'),
    ('blue', 'BLUE'),
    ('red', 'RED'),
    ('orange', 'ORANGE'),
    ('black', 'BLACK'),
)

class MyModel(models.Model):
    color = models.CharField(max_length=6, choices=COLOR_CHOICES, default='green')





