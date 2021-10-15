import datetime
from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render

from .models import Point, Strizh, DroneJournal, AeroPoints, DroneTrajectoryJournal, SkyPoint, StrigState


def geojson_view(request):
    geom_as_geojson = serialize('geojson', Point.objects.all().order_by('-current_time'))
    return HttpResponse(geom_as_geojson, content_type='geojson')


def drone_journal_view(request):
    drone_as_geojson = serialize('geojson', DroneJournal.objects.all().order_by('-pk'))
    return HttpResponse(drone_as_geojson, content_type='geojson')


def drone_journal_view_traj(request):
    drone_as_geojson = serialize('geojson', DroneTrajectoryJournal.objects.all().order_by('-current_time'))
    return HttpResponse(drone_as_geojson, content_type='geojson')


def journal_view_aero_main(request):
    time_now = datetime.datetime.now()
    time_delta = int(time_now.minute) - 10
    low_min = time_delta if 0 < time_delta < 60 else 0
    time_border = time_now.replace(minute=low_min).strftime('%Y-%m-%d %H:%M:%S')

    QuerySkypoints = AeroPoints.objects.all().filter(current_time__gte=time_border).order_by('-current_time')
    drone_as_geojson = serialize('geojson', QuerySkypoints)
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


def conditions_view(request):
    Conditions = serialize('geojson', StrigState.objects.all().order_by('pk'))
    return HttpResponse(Conditions, content_type='geojson')
