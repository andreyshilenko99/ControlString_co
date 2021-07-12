from django.contrib import admin
from geo.models import Point, Strizh, Sector
# from map.models import MyStrizh


class Inc(admin.ModelAdmin):
    # list_display = ('name','mpoint')
    list_display = ('name')


admin.site.register(Point)
admin.site.register(Strizh)
admin.site.register(Sector)

