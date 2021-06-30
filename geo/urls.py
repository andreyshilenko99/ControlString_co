from django.conf.urls import url
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView
from geo import models
from .views import geojson_view, geo_govno

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='test.html'), name='home'),
    url(r'^data.geojson$', GeoJSONLayerView.as_view(model=models.Point), name='data'),
    url(r'data/', geojson_view, name='data_json'),
    url(r'geo_govno', geo_govno),
]
