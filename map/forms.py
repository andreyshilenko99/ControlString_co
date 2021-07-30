import django.forms
from django.forms import ModelForm, Select, ModelChoiceField, ModelMultipleChoiceField, CharField, IntegerField, \
    TextInput
from django.forms import CheckboxSelectMultiple

from geo.models import Strizh, Point, DroneJournal, StrizhJournal, ApemsConfiguration
# from django.forms import widgets
from django import forms

from django.forms import IntegerField, TextInput, NumberInput

class StrizhForm(ModelForm):
    chosen_strizh = ModelChoiceField(queryset=Strizh.objects.all(), empty_label="Выберите стрижа",
                                     required=False, to_field_name="name",
                                     label="")

    class Meta:
        model = Strizh
        fields = ['chosen_strizh']
        widgets = {
            'chosen_strizh': Select(attrs={'id': 'name'}),
        }


class StrizhFilterForm(ModelForm):
    filtered_strizhes = ModelMultipleChoiceField(queryset=Strizh.objects.all(),
                                                 required=False, to_field_name="name",
                                                 label="")

    class Meta:
        model = Strizh
        fields = ['filtered_strizhes']
        widgets = {
            'filtered_strizhes': Select(attrs={'id': 'name', 'width': '300px',
                                               'class': 'myfieldclass'}),

        }


class DroneFilterForm(ModelForm):
    names_arr = []
    AllDrones = Point.objects.all().order_by('-detection_time')
    drone_toshow = ModelMultipleChoiceField(queryset=AllDrones,
                                            required=False, to_field_name="pk",
                                            label="")

    class Meta:
        model = Point
        fields = ['drone_toshow']
        widgets = {
            'filtered_strizhes': Select(attrs={'id': 'name', 'size': '10',
                                               }),
        }




class ApemsConfigurationForm(ModelForm):

    AllApems = ApemsConfiguration.objects.all().order_by('-freq_podavitelya')
    apem_toshow = ModelMultipleChoiceField(queryset=AllApems,
                                           required=False, to_field_name="pk",
                                           label="",
                                           )
    # apem_toshow.widget = Select(attrs={'size': 12, 'id': 'block2'
    #                        })

    class Meta:
        model = ApemsConfiguration
        fields = ['apem_toshow']
        widget = {
            'apem_toshow': Select(attrs={'id': 'block2', 'size': 10,
                                         }),
        }


class ApemsChangingForm(ModelForm):
    AllApems = ApemsConfiguration.objects.all().order_by('-freq_podavitelya')

    class Meta:
        model = ApemsConfiguration
        fields = ['freq_podavitelya', 'deg_podavitelya', 'type_podavitelya',
                  'type_podavitelya', 'ip_podavitelya', 'canal_podavitelya', 'usileniye_db'
                  ]
        widgets = {
            'freq_podavitelya': NumberInput(attrs={'class': 'form-control', 'required': 'False',
                                                   'placeholder': 'Частота подавителя'}),
            'deg_podavitelya': NumberInput(attrs={'class': 'form-control',
                                                  'placeholder': 'Номер подавителя (60, 120 ...)'}),
            'type_podavitelya': Select(attrs={'class': 'form-control', 'placeholder': 'Тип подавителя'}),
            'ip_podavitelya': TextInput(attrs={'class': 'form-control', 'placeholder': 'IP-адрес подавителя'}),
            'canal_podavitelya': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Канал подавителя'}),
            'usileniye_db': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Усиление, дб'}),
        }

# freq_podavitelya = models.CharField('Частота подавителя', max_length=500, default=' ')
# deg_podavitelya = IntegerRangeField('Номер подавителя (60, 120 ...)', default=0, min_value=0, max_value=300)
#
# type_podavitelya = models.CharField('Тип подавителя', max_length=500, choices=PODAVITEL_CHOICES)
# ip_podavitelya = models.GenericIPAddressField('IP-адрес подавителя')
# canal_podavitelya = IntegerRangeField('Канал подавителя', default=0, min_value=0, max_value=2)
# usileniye_db = IntegerRangeField('Усиление', default=0, min_value=0, max_value=31)
