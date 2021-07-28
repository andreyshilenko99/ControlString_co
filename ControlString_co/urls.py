"""ControlString_co URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from geo.views import geojson_view
from map import views
from django.http import HttpResponseRedirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('geo/', include('geo.urls')),
    # # path(r' ', include('map.urls'))
    # path(r'', include('geo.urls')),

    path('', views.index),
    path('menu', views.index),
    # path('main', views.CreateMyModelView.as_view()),
    path('main', views.render_main_page),
    path('back2main', views.back2main),

    path('journal', views.journal),
    path('filter_nomer_strizha', views.filter_nomer_strizha),
    path('choose_drone_toshow', views.choose_drone_toshow),
    path('reset_filter', views.reset_filter),
    path('reset_filter_strizh', views.reset_filter_strizh),
    path('export_csv', views.export_csv),
    path('filter_all', views.filter_all),

    path('configuration', views.configuration),
    path('butt_skan_all', views.butt_skan_all),
    path('butt_glush_all', views.butt_glush_all),
    path('butt_gps_all', views.butt_gps_all),
    path('butt_ku_all', views.butt_ku_all),
    path('choose_nomer_strizha', views.choose_nomer_strizha),
    path('choose_all_strizhes', views.choose_all_strizhes),

    path(r'strizh_view', geojson_view),

    # path(r'get_drones', views.get_drones),

    # path(r'update_nomer_strizha', views.update_nomer_strizha),
    path('butt_skan', views.butt_skan),
    path('butt_glush', views.butt_glush),
    path('butt_gps', views.butt_gps),
    path('butt_ku', views.butt_ku),
    path('apply_period', views.apply_period),
    # path('get_conditions', views.get_conditions),
    path('turn_on_bp', views.turn_on_bp),
    path('turn_off_bp', views.turn_off_bp),
    # path('functioning_loop', views.functioning_loop),
    path('show_logs', views.show_logs),

    path('choose_apem_toshow', views.choose_apem_toshow),

]
