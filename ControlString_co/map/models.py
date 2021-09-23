from django.db import models
import datetime

class TimePick(models.Model):
    # datetime = models.DateTimeField()
    time_now = datetime.datetime.now()
    d_st = time_now.replace(year=2020)
    d_end = time_now.replace(year=2050)
    datetime_start = models.DateTimeField(blank=True, default=d_st)
    datetime_end = models.DateTimeField(blank=True, default=d_end)

    def __str__(self):
        return '{} --- {}'.format(self.datetime_start, self.datetime_end)

    class Meta:
        verbose_name = 'Время'
        verbose_name_plural = 'Время'




