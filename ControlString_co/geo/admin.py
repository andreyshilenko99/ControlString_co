from django.contrib import admin
from geo.models import Point, Strizh, ApemsConfiguration, AeroPoints


# from map.models import MyStrizh

class Inc(admin.ModelAdmin):
    # list_display = ('name','mpoint')
    list_display = ('name')


admin.site.register(Point)
admin.site.register(Strizh)
admin.site.register(ApemsConfiguration)
admin.site.register(AeroPoints)

from django.apps import apps

var = apps.get_app_config('admin').verbose_name
