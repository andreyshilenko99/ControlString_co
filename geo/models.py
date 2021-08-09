from django.contrib.gis.db import models


class Point(models.Model):
    system_name = models.CharField('Имя дрона', max_length=500)
    center_freq = models.FloatField('Несущая частота')
    brandwidth = models.FloatField('Пропускная способность')
    detection_time = models.CharField('Время обнаружения', max_length=500)
    comment_string = models.CharField('Комментарии', max_length=500)
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    azimuth = models.CharField('Азимут', max_length=500)
    area_sector_start_grad = models.FloatField('Внутренний радиус сектора')
    area_sector_end_grad = models.FloatField('Внешний радиус сектора')
    area_radius_m = models.FloatField('Радиус сектора (м)')
    ip = models.CharField('IP-адрес стрижа', max_length=500)
    current_time = models.CharField('Время засечки', max_length=500, default='')
    strig_name = models.CharField('Имя стрижа', max_length=500, default='')

    def __str__(self):
        prop_spos = 'Пропускная способность: {} МГц'.format(round(self.brandwidth, 2))
        arr_to_return = [self.detection_time, self.system_name, str(int(self.area_sector_start_grad)) + '°-' +
                         str(int(self.area_sector_end_grad)) + '° ', self.azimuth, 'host:', self.ip,
                         self.strig_name, prop_spos, self.comment_string,
                         str(int(self.area_radius_m)) + 'м.']
        arr_strings = [str(el) for el in arr_to_return]

        str_to_return = ', '.join(arr_strings)
        return str_to_return

    class Meta:
        verbose_name_plural = 'Дроны'
        verbose_name = 'Дрон'


class DroneJournal(models.Model):
    system_name = models.CharField('Имя дрона', max_length=500)
    center_freq = models.FloatField('Несущая частота')
    brandwidth = models.FloatField('Пропускная способность')
    detection_time = models.CharField('Время обнаружения', max_length=500)
    comment_string = models.CharField('Комментарии', max_length=500)
    lat = models.FloatField('Широта')
    lon = models.FloatField('Долгота')
    azimuth = models.CharField('Азимут', max_length=500)
    area_sector_start_grad = models.FloatField('Внутренний радиус сектора')
    area_sector_end_grad = models.FloatField('Внешний радиус сектора')
    area_radius_m = models.FloatField('Радиус сектора (м)')
    ip = models.CharField('IP-адрес стрижа', max_length=500)
    current_time = models.CharField('Время засечки', max_length=500, default='')
    strig_name = models.CharField('Имя стрижа', max_length=500, default='')

    def __str__(self):
        prop_spos = 'Bandwidth: {} МГц'.format(round(self.brandwidth, 2))
        arr_to_return = [self.detection_time, self.system_name, int(self.area_sector_start_grad), '° -',
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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Стриж'
        verbose_name_plural = 'Стрижи'
        ordering = ['name']


class StrizhJournal(models.Model):
    filtered_strizhes = models.CharField('Нужные стрижи', max_length=500, default='стриж 0 (по умолчанию)')
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

from django.db import models


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


class ApemsConfiguration(models.Model):
    CHOICES_STRIZH = Strizh.objects.all()
    strizh_name = models.CharField('Имя стрижа', max_length=500, choices=((x.name, x.name) for x in CHOICES_STRIZH),
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
