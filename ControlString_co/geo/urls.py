from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView

# from django.contrib.gis.db import models
from geo import models

from geo.views import geojson_view, conditions_view, drone_journal_view, skypoint_view, strizh_view, journal_view_aero, \
    journal_view_aero_main, drone_journal_view_traj
from map.views import journal_view, filter_all

urlpatterns = [
    url(r'data/', geojson_view, name='data_json'),
    url(r'filter_all/', filter_all, name='filter_all'),
    url(r'journal_view/', journal_view, name='datajournal_json'),
    url(r'journal_view_aero/', journal_view_aero, name='journal_view_aero_json'),
    url(r'journal_view_aero_main/', journal_view_aero_main, name='journal_view_aero_main'),
    url(r'drone_journal/', drone_journal_view, name='drone_journal'),
    url(r'drone_journal_view_traj/', drone_journal_view_traj, name='drone_journal_view_traj'),
    url(r'strizh_view/', strizh_view, name='strizh_view'),
    url(r'skypoint_view/', skypoint_view, name='strizh_view'),
    url(r'conditions_view/', conditions_view, name='conditions_view'),

]
