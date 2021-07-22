from django.contrib import admin
from geo.models import Point, Strizh


# from map.models import MyStrizh


class Inc(admin.ModelAdmin):
    # list_display = ('name','mpoint')
    list_display = ('name')


admin.site.register(Point)
admin.site.register(Strizh)



from django.apps import apps

var = apps.get_app_config('admin').verbose_name
