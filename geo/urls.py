from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView

# from django.contrib.gis.db import models
from geo import models

from geo.views import geojson_view, geo_govno, new_coords, strizh_coords, strizh_view, sector_view, sector_coords


urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='test.html'), name='home'),
    # url(r'^data.geojson$', GeoJSONLayerView.as_view(model=models.PointStrizh), name='data'),
    url(r'data/', geojson_view, name='data_json'),
    url(r'new_coords/', new_coords, name='new_coords_json'),
    url(r'strizh_view/', strizh_view, name='strizh_view'),
    url(r'strizh_coords/', strizh_coords, name='strizh_coords_json'),
    url(r'sector_view/', sector_view, name='sector_view'),
    url(r'sector_coords/', sector_coords, name='sector_coords_json'),
    url(r'geo_govno', geo_govno)
]


