from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from djgeojson.views import GeoJSONLayerView
from map import views

# from .models import MushroomSpot

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='test.html'), name='home'),
    path('export', views.export, name='export')]
#     url(r'^data.geojson$',
#         GeoJSONLayerView.as_view(model=MushroomSpot, properties=('title', 'description', 'picture_url')),
#         name='data')
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)