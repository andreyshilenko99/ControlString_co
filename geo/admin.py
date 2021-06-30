from django.contrib import admin
# from geo.models import Point


class Inc(admin.ModelAdmin):
    list_display = ('name','mpoint')


# admin.site.register(Point, Inc)

# from .models import MushroomSpot
# from leaflet.admin import LeafletGeoAdmin
# from django.contrib import admin
#
# admin.site.register(MushroomSpot, LeafletGeoAdmin)
