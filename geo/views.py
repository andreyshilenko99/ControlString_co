from django.core.serializers import serialize
from django.http import HttpResponse

from .models import Point, Strizh, Sector


# , LoadDict


def geojson_view(request):
    # geom_as_geojson = serialize('geojson', Point.objects.all().order_by('-pk'))
    geom_as_geojson = serialize('geojson', Point.objects.all().order_by('-detection_time'))
    return HttpResponse(geom_as_geojson, content_type='geojson')


def new_coords(request):
    # send coords to BD
    fuckingshit = Point(name="dron3", lat=60.01450757958334,
                        lon=30.453994274139404)
    fuckingshit.save()
    geom_as_geojson = serialize('geojson', Point.objects.all())
    # return HttpResponse(geom_as_geojson, content_type='geojson')
    return render(request, 'test.html')


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


def sector_coords(request):
    sector_c = Sector(name="strizh1", center_lat=60.014375,
                      center_lon=30.448045, innerRadius=0, outerRadius=500,
                      startBearing=-30, endBearing=30)
    sector_c.save()
    geom_as_geojson = serialize('geojson', Sector.objects.all())
    return HttpResponse(geom_as_geojson, content_type='geojson')


def sector_view(request):
    geom_as_geojson = serialize('geojson', Sector.objects.all())
    return HttpResponse(geom_as_geojson, content_type='geojson')


from django.shortcuts import render


# from .models import Location
#
def geo_govno(request):
    # location = Location.objects.get(id=1)
    # location_json = location.serialize()
    # context = {
    #     'location1': location_json
    # }
    return render(request, '../templates/test.html')
