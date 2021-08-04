from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView

# from django.contrib.gis.db import models
from geo import models

from geo.views import geojson_view, drone_journal_view, strizh_coords, strizh_view

urlpatterns = [
    url(r'data/', geojson_view, name='data_json'),
    url(r'drone_journal/', drone_journal_view, name='drone_journal'),
    url(r'strizh_view/', strizh_view, name='strizh_view'),
    url(r'strizh_coords/', strizh_coords, name='strizh_coords_json'),
]
