from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render
from .models import Point


def geojson_view(request):
    geom_as_geojson = serialize('geojson', Point.objects.all())
    return HttpResponse(geom_as_geojson, content_type='json')

from django.shortcuts import render
from .models import Location

def geo_govno(request):
    location = Location.objects.get(id=2)
    location_json = location.serialize()
    context = {
        'location1': location_json
    }
    return render(request, '../templates/test.html', context)

# def geo_govno(request):
#     from json import dumps
#     locations = Location.objects.all()
#     location_list = [l.serialize() for l in locations]
#     location_dict = {
#         "type": "FeatureCollection",
#         "features": location_list
#     }
#     location_json = dumps(location_dict)
#
#     context = {
#         'locations': location_json,
#     }
#     return render(request, '../templates/test.html', context)