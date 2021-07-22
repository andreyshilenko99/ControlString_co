from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render

from .models import Point, Strizh, DroneJournal


def geojson_view(request):
    # geom_as_geojson = serialize('geojson', Point.objects.all().order_by('-pk'))
    geom_as_geojson = serialize('geojson', Point.objects.all().order_by('-detection_time'))
    return HttpResponse(geom_as_geojson, content_type='geojson')


def drone_journal_view(request):
    # geom_as_geojson = serialize('geojson', Point.objects.all().order_by('-pk'))
    drone_as_geojson = serialize('geojson', DroneJournal.objects.all().order_by('-pk'))
    return HttpResponse(drone_as_geojson, content_type='geojson')


def strizh_coords(request):
    strizh_c = Strizh(name="strizh1", lat=60.014375,
                      lon=30.448045)
    strizh_c.save()
    geom_as_geojson = serialize('geojson', Strizh.objects.all())
    return HttpResponse(geom_as_geojson, content_type='geojson')
    # return render(request, 'test.html')


def strizh_view(request):
    geom_as_geojson = serialize('geojson', Strizh.objects.all())
    return HttpResponse(geom_as_geojson, content_type='geojson')
