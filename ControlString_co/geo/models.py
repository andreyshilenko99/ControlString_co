from django.contrib.gis.db import models
import django.contrib.gis.db.models as M
import datetime

from django.db import models
from django.apps import apps
import django.contrib.gis.geos as G
from django.contrib.postgres.fields import ArrayField


class Point(models.Model):
    drone_id = models.CharField('Идентификатор дрона', default='', max_length=500)
    system_name = models.CharField('Имя дрона', max_length=500)
    center_freq = models.FloatField('Несущая частота')
    brandwidth = models.FloatField('Пропускная способность')
    detection_time = models.CharField('Время обнаружения', max_length=500)
    comment_string = models.CharField('Комментарии', max_length=500)
    drone_lat = models.FloatField('Широта')
    drone_lon = models.FloatField('Долгота')
    remote_lat = models.FloatField('Широта пульта', default=0)
    remote_lon = models.FloatField('Долгота пульта', default=0)
    azimuth = models.CharField('Азимут', max_length=500)
    area_sector_start_grad = models.FloatField('Внутренний радиус сектора')
    area_sector_end_grad = models.FloatField('Внешний радиус сектора')
    area_radius_m = models.FloatField('Радиус сектора (м)', default=None)
    ip = models.CharField('IP-адрес стрижа', max_length=500)
    current_time = models.CharField('Время засечки', max_length=500, default='')
    height = models.FloatField('Высота (м)', default='')
    strig_name = models.CharField('Имя стрижа', max_length=500, default='')

    def __str__(self):
        prop_spos = 'Пропускная способность: {} МГц'.format(round(self.brandwidth, 2))
        arr_to_return = [self.current_time, self.system_name, str(int(self.area_sector_start_grad)) + '°-' +
                         str(int(self.area_sector_end_grad)) + '° ', self.azimuth, 'host:', self.ip,
                         self.strig_name, prop_spos, self.comment_string,
                         str(int(self.area_radius_m)) + 'м.']
        arr_strings = [str(el) for el in arr_to_return]

        str_to_return = ', '.join(arr_strings)
        # return str_to_return
        return str(self.current_time)

    class Meta:
        verbose_name_plural = 'Дроны'
        verbose_name = 'Дрон'


class AeroPoints(models.Model):
    drone_id = models.CharField('Идентификатор дрона', default='0', max_length=500)
    system_name = models.CharField('Имя дрона', max_length=500, default='')
    center_freq = models.FloatField('Несущая частота', default=0)
    brandwidth = models.FloatField('Пропускная способность', default=0)
    detection_time = models.CharField('Время обнаружения', max_length=500)
    comment_string = models.CharField('Комментарии', max_length=500, default='')
    # lat = models.FloatField('Широта')
    # lon = models.FloatField('Долгота')
    # drone_coords = ArrayField(ArrayField(models.FloatField(max_length=10)))
    drone_lat = models.FloatField(max_length=10, default=0)
    drone_lon = models.FloatField(max_length=10, default=0)
    remote_lat = models.FloatField('Широта пульта', default=0)
    remote_lon = models.FloatField('Долгота пульта', default=0)
    azimuth = models.CharField('Азимут', max_length=500, default='')
    area_sector_start_grad = models.FloatField('Внутренний радиус сектора', default=0)
    area_sector_end_grad = models.FloatField('Внешний радиус сектора', default=0)
    area_radius_m = models.FloatField('Радиус сектора (м)', default=0)
    ip = models.CharField('IP-адрес стрижа', max_length=500, default='')
    current_time = models.CharField('Время засечки', max_length=500, default='')
    height = models.FloatField('Высота (м)', default=0)
    strig_name = models.CharField('Имя устройства', max_length=500, default='')

    def __str__(self):
        # prop_spos = 'Пропускная способность: {} МГц'.format(round(self.brandwidth, 2))
        # arr_to_return = [self.detection_time, self.system_name, str(int(self.area_sector_start_grad)) + '°-' +
        #                  str(int(self.area_sector_end_grad)) + '° ', self.azimuth, 'host:', self.ip,
        #                  self.strig_name, prop_spos, self.comment_string,
        #                  str(int(self.area_radius_m)) + 'м.']
        # arr_strings = [str(el) for el in arr_to_return]
        #
        # str_to_return = ', '.join(arr_strings)
        return str(self.system_name)

    class Meta:
        verbose_name_plural = 'Аэропупы'
        verbose_name = 'Аэропуп'


class DroneJournal(models.Model):
    drone_id = models.CharField('Идентификатор дрона', default='0', max_length=500)
    system_name = models.CharField('Имя дрона', max_length=500, default='')
    center_freq = models.FloatField('Несущая частота', default=0)
    brandwidth = models.FloatField('Пропускная способность', default=0)
    detection_time = models.CharField('Время обнаружения', max_length=500)
    comment_string = models.CharField('Комментарии', max_length=500, default='')
    # lat = models.FloatField('Широта')
    # lon = models.FloatField('Долгота')
    # drone_coords = ArrayField(ArrayField(models.FloatField(max_length=10)))
    drone_lat = models.FloatField(max_length=10, default=0)
    drone_lon = models.FloatField(max_length=10, default=0)
    remote_lat = models.FloatField('Широта пульта', default=0)
    remote_lon = models.FloatField('Долгота пульта', default=0)
    azimuth = models.CharField('Азимут', max_length=500, default='')
    area_sector_start_grad = models.FloatField('Внутренний радиус сектора', default=0)
    area_sector_end_grad = models.FloatField('Внешний радиус сектора', default=0)
    area_radius_m = models.FloatField('Радиус сектора (м)', default=0)
    ip = models.CharField('IP-адрес стрижа', max_length=500, default='')
    current_time = models.CharField('Время засечки', max_length=500, default='')
    height = models.FloatField('Высота (м)', default=0)
    strig_name = models.CharField('Имя устройства', max_length=500, default='')

    def __str__(self):
        prop_spos = 'Bandwidth: {} МГц'.format(round(self.brandwidth, 2))
        arr_to_return = [self.current_time, self.system_name, int(self.area_sector_start_grad), '° -',
                         int(self.area_sector_end_grad), '° ', self.azimuth, 'host:' + str(self.ip),
                         self.strig_name, prop_spos, self.comment_string,
                         self.area_radius_m, 'м.']
        arr_strings = [str(el) for el in arr_to_return]

        str_to_return = ', '.join(arr_strings)
        return str_to_return

    class Meta:
        verbose_name_plural = 'Дроны'
        verbose_name = 'Дрон'


class DroneTrajectoryJournal(models.Model):
    drone_id = models.CharField('Идентификатор дрона', default='0', max_length=500)
    system_name = models.CharField('Имя дрона', max_length=500, default='')
    center_freq = models.FloatField('Несущая частота', default=0)
    brandwidth = models.FloatField('Пропускная способность', default=0)
    detection_time = models.CharField('Время обнаружения', max_length=500)
    comment_string = models.CharField('Комментарии', max_length=500, default='')
    # lat = models.FloatField('Широта')
    # lon = models.FloatField('Долгота')
    # drone_coords = ArrayField(ArrayField(models.FloatField(max_length=10)))
    drone_lat = models.FloatField(max_length=10, default=0)
    drone_lon = models.FloatField(max_length=10, default=0)
    remote_lat = models.FloatField('Широта пульта', default=0)
    remote_lon = models.FloatField('Долгота пульта', default=0)
    azimuth = models.CharField('Азимут', max_length=500, default='')
    area_sector_start_grad = models.FloatField('Внутренний радиус сектора', default=0)
    area_sector_end_grad = models.FloatField('Внешний радиус сектора', default=0)
    area_radius_m = models.FloatField('Радиус сектора (м)', default=0)
    ip = models.CharField('IP-адрес стрижа', max_length=500, default='')
    current_time = models.CharField('Время засечки', max_length=500, default='')
    height = models.FloatField('Высота (м)', default=0)
    strig_name = models.CharField('Имя устройства', max_length=500, default='')

    def __str__(self):
        prop_spos = 'Bandwidth: {} МГц'.format(round(self.brandwidth, 2))
        arr_to_return = [self.current_time, self.system_name, int(self.area_sector_start_grad), '° -',
                         int(self.area_sector_end_grad), '° ', self.azimuth, 'host:' + str(self.ip),
                         self.strig_name, prop_spos, self.comment_string,
                         self.area_radius_m, 'м.']
        arr_strings = [str(el) for el in arr_to_return]

        str_to_return = ', '.join(arr_strings)
        return str_to_return

    class Meta:
        verbose_name_plural = 'Дроны'
        verbose_name = 'Дрон'


class Strizh(models.Model):
    name = models.CharField('Имя стрижа', max_length=500, default='стриж 0 (по умолчанию)')
    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)
    ip1 = models.CharField('IP-адрес стрижа (хост 1)', max_length=500, default='')
    ip2 = models.CharField('IP-адрес стрижа (хост 2)', max_length=500, default='')
    uniping_ip = models.CharField('IP-адрес Uniping', max_length=500, default='')
    radius = models.FloatField('Радиус', blank=True, null=True, default=500)
    seconds_drone_show = models.IntegerField('Длительность отображения дрона', default=10)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Стриж'
        verbose_name_plural = 'Стрижи'
        ordering = ['name']


class SkyPoint(models.Model):
    name = models.CharField('Имя устройства', max_length=500, default='Скайпоинт 0 (по умолч.)')
    lat = models.FloatField('Широта', blank=True, null=True)
    lon = models.FloatField('Долгота', blank=True, null=True)
    ip = models.CharField('IP', max_length=500, default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Скайпоинт'
        verbose_name_plural = 'Скайпоинты'
        ordering = ['name']


class StrizhJournal(models.Model):
    filtered_strizhes = models.CharField('Нужные стрижи', max_length=500, default='стриж 0 (по умолч.)')
    filtered_skypoints = models.CharField('Нужные skypoints', max_length=500, default='skypoint 0 (по умолч.)')
    start_datetime = models.CharField('Время начала', max_length=50, blank=True, null=True)
    end_datetime = models.CharField('Время конца', max_length=50, blank=True, null=True)
    print(filtered_strizhes)

    def __str__(self):
        return str(self.filtered_strizhes)

    class Meta:
        verbose_name = 'Отфильтрованные стрижи'
        # verbose_name_plural = 'Стрижи'
        ordering = ['-pk']


PODAVITEL_CHOICES = (
    ('АПЕМ (Многоканальный)', 'АПЕМ (Многоканальный)'),
    ('Тестовый модуль', 'Тестовый модуль'),
    ('Шелест', 'Шелест'),
    ('Шелест (Многоканальный)', 'Шелест (Многоканальный)'),
    ('BarGen (Enter Morph)', 'BarGen (Enter Morph)'),
    ('BarGen (Плата Б)', 'BarGen (Плата Б)'),
)


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


class ApemsConfiguration(models.Model):
    # CHOICES_STRIZH = Strizh.objects.all()
    # strizh_name = models.CharField('Имя стрижа', max_length=500, choices=((x.name, x.name) for x in CHOICES_STRIZH),
    #                                error_messages={'required': ''}
    #                                )
    strizh_name = models.CharField('Имя стрижа', max_length=500, default='стриж 0 (по умолчанию)',
                                   error_messages={'required': ''}
                                   )

    freq_podavitelya = IntegerRangeField('Частота подавителя', default=2400, min_value=2400, max_value=6000,
                                         error_messages={'required': ''}
                                         )
    deg_podavitelya = IntegerRangeField('Номер подавителя (60, 120 ...)', default=60, min_value=0, max_value=300,
                                        error_messages={'required': ''}
                                        )
    # name_podavitelya = models.CharField('Имя подавителя', max_length=500, default='qwd ')
    type_podavitelya = models.CharField('Тип подавителя', max_length=500, choices=PODAVITEL_CHOICES,
                                        error_messages={'required': ''}
                                        )
    ip_podavitelya = models.GenericIPAddressField('IP-адрес подавителя', max_length=500, default='192.168.2.121',
                                                  error_messages={'required': ''})
    canal_podavitelya = IntegerRangeField('Канал подавителя', default=0, min_value=0, max_value=2,
                                          error_messages={'required': ''}
                                          )
    usileniye_db = IntegerRangeField('Усиление', default=0, min_value=0, max_value=31, error_messages={'required': ''}
                                     )

    def __str__(self):
        str_to_return = str(self.freq_podavitelya) + ' - ' + str(self.deg_podavitelya) + '° ' + str(
            self.type_podavitelya) + \
                        ' ' + str(self.usileniye_db) + 'db'
        return str_to_return

    class Meta:
        verbose_name = 'Конфигурация АПЕМ'
        verbose_name_plural = 'АПЕМы'
        ordering = ['-freq_podavitelya']


class TimePick(models.Model):
    time_now = datetime.datetime.now()
    # d_st = time_now.replace(year=2020).strftime('%Y-%m-%d %H:%M:%S')
    # d_end = time_now.replace(year=2050).strftime('%Y-%m-%d %H:%M:%S')
    d_st = '2000-01-01 00:00:01'
    d_end = '2100-01-01 00:00:01'
    datetime_start = models.DateTimeField(blank=True, default=d_st)
    datetime_end = models.DateTimeField(blank=True, default=d_end)

    def __str__(self):
        return '{} --- {}'.format(self.datetime_start, self.datetime_end)

    class Meta:
        verbose_name = 'Время'
        verbose_name_plural = 'Время'


class Maps(models.Model):
    # datetime = models.DateTimeField()
    map_link = models.CharField('Источник тайлов для карты (z/x/y)', max_length=500,
                                default='http://localhost:8000/static/spb_osm_new/{z}/{x}/{y}.png',
                                error_messages={'required': ''}
                                )
    map_name = models.CharField('название карты', max_length=500,
                                default='Спутниковая съемка',
                                error_messages={'required': ''}
                                )

    def __str__(self):
        return '{} {}'.format(self.map_name, self.map_link)

    class Meta:
        verbose_name = 'Карта'
        verbose_name_plural = 'Карты'


class StrigState(models.Model):
    strig_name = models.CharField(max_length=500)
    ip1_state = models.CharField(max_length=500)
    ip2_state = models.CharField(max_length=500)
    temperature = models.CharField(max_length=500)
    temperature_state = models.CharField(max_length=500)
    wetness = models.CharField(max_length=500)
    wetness_state = models.CharField(max_length=500)
    cooler = models.CharField(max_length=500)

    def __str__(self):
        return self.strig_name

    class Meta:
        verbose_name = 'Состояние стрижа'
        verbose_name_plural = 'Состояния стрижей'
