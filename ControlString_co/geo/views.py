from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render

from .models import Point, Strizh, DroneJournal, AeroPoints, DroneTrajectoryJournal, SkyPoint


def geojson_view(request):
    geom_as_geojson = serialize('geojson', Point.objects.all().order_by('-detection_time'))
    return HttpResponse(geom_as_geojson, content_type='geojson')


def drone_journal_view(request):
    drone_as_geojson = serialize('geojson', DroneJournal.objects.all().order_by('-pk'))
    return HttpResponse(drone_as_geojson, content_type='geojson')


def drone_journal_view_traj(request):
    drone_as_geojson = serialize('geojson', DroneTrajectoryJournal.objects.all().order_by('-pk'))
    return HttpResponse(drone_as_geojson, content_type='geojson')


def journal_view_aero(request):
    drone_as_geojson = serialize('geojson', AeroPoints.objects.all().order_by('-pk'))
    return HttpResponse(drone_as_geojson, content_type='geojson')


def strizh_view(request):
    geom_as_geojson = serialize('geojson', Strizh.objects.all())
    return HttpResponse(geom_as_geojson, content_type='geojson')

def skypoint_view(request):
    SkyPoint_as_geojson = serialize('geojson', SkyPoint.objects.all().order_by('-pk'))
    return HttpResponse(SkyPoint_as_geojson, content_type='geojson')
