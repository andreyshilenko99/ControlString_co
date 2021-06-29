from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render
from .models import Point


def geojson_view(request):
    geom_as_geojson = serialize('geojson', Point.objects.all())
    return HttpResponse(geom_as_geojson, content_type='json')
