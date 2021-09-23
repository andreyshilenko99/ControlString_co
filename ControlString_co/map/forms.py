import django.forms
from django.forms import ModelForm, Select, ModelChoiceField, ModelMultipleChoiceField, CharField, IntegerField, \
    TextInput, SelectMultiple
from django.forms import CheckboxSelectMultiple

from geo.models import Strizh, Point, DroneJournal, StrizhJournal, ApemsConfiguration, SkyPoint
# from django.forms import widgets

from django.forms import IntegerField, TextInput, NumberInput, ModelForm
from django import forms

from .models import TimePick


class TimePickForm(ModelForm):
    datetime_start = forms.DateTimeInput(format='%Y-%m-%d %H:%M')
    datetime_end = forms.DateTimeInput(format='%Y-%m-%d %H:%M')

    class Meta:
        model = TimePick
        fields = ['datetime_start', 'datetime_end']
        widgets = {
            'datetime_start': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'datetime_end': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'})
        }


class StrizhForm(ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    # self.initial['chosen_strizh'] = None
    # self.initial['chosen_strizh'] = kwargs.get('initial', None)
    # self.fields['chosen_strizh'].initial = kwargs.get('initial', None)
    chosen_strizh = ModelChoiceField(queryset=Strizh.objects.all(), empty_label="Выберите стрижа",
                                     required=False, to_field_name="name",
                                     label="", widget=Select(attrs={'id': 'name', 'onchange': 'submit();'}))

    class Meta:
        model = Strizh
        fields = ['chosen_strizh']


class StrizhFilterForm(ModelForm):
    filtered_strizhes = ModelMultipleChoiceField(queryset=Strizh.objects.all(),
                                                 required=False, to_field_name="name",
                                                 label="")
    filtered_strizhes.widget = SelectMultiple(attrs={'id': 'choose_strizh', 'size': '4', 'class': 'myfieldclass',
                                                     'onchange': 'submit();'})

    class Meta:
        model = Strizh
        fields = ['filtered_strizhes']


class SkyPointFilterForm(ModelForm):
    filtered_skypoints = ModelMultipleChoiceField(queryset=SkyPoint.objects.all(),
                                                  required=False, to_field_name="name",
                                                  label="")
    filtered_skypoints.widget = SelectMultiple(attrs={'id': 'choose_skypoint', 'size': '4', 'class': 'myfieldclass',
                                                      'onchange': 'submit();'
                                                      })

    class Meta:
        model = Strizh
        fields = ['filtered_skypoints']


class DroneFilterForm(ModelForm):
    names_arr = []
    AllDrones = Point.objects.all().order_by('-detection_time')
    drone_toshow = ModelMultipleChoiceField(queryset=AllDrones,
                                            required=False, to_field_name="pk",
                                            label="")
    drone_toshow.widget = SelectMultiple(attrs={'id': 'detections', 'size': '8',
                                                })

    class Meta:
        model = Point
        fields = ['drone_toshow']


class TableFilterForm(ModelForm):
    zz = Point._meta.get_fields()
    AllFields = tuple([(f.name, f.verbose_name) for f in Point._meta.get_fields()])
    field = forms.ChoiceField(choices=AllFields, required=False,
                              label="", initial="detection_time",
                              widget=Select(attrs={'id': 'name', 'onchange': 'submit();'}))

    class Meta:
        model = Point
        fields = ['field']


class TableOrderForm(ModelForm):
    zz = Point._meta.get_fields()
    AllFields = tuple([('-', 'по убыванию'), ('+', 'по возрастанию')])
    order_sign = forms.ChoiceField(choices=AllFields, required=False, initial="-",
                                   label="", widget=forms.Select(attrs={'onchange': 'submit();'}))

    class Meta:
        model = Point
        fields = ['order_sign']


class ApemsConfigurationForm(ModelForm):
    AllApems = ApemsConfiguration.objects.all().order_by('-freq_podavitelya')
    apem_toshow = ModelMultipleChoiceField(queryset=AllApems,
                                           required=False, to_field_name="pk",
                                           label="",
                                           )
    apem_toshow.widget = SelectMultiple(attrs={'size': 12, 'id': 'block1', 'onchange': 'submit();'
                                               })

    class Meta:
        model = ApemsConfiguration
        fields = ['apem_toshow']


#         widgets = {
#             'apem_toshow': Select(attrs={'size': 12, 'id': 'block2'
#                            })
# ,
#         }


class ApemsChangingForm(ModelForm):
    AllApems = ApemsConfiguration.objects.all().order_by('-freq_podavitelya')

    class Meta:
        CHOICES = Strizh.objects.all()
        model = ApemsConfiguration
        fields = ['strizh_name', 'freq_podavitelya', 'deg_podavitelya', 'type_podavitelya',
                  'type_podavitelya', 'ip_podavitelya', 'canal_podavitelya', 'usileniye_db'
                  ]

        widgets = {
            'strizh_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя стрижа'}),
            'freq_podavitelya': NumberInput(attrs={'class': 'form-control', 'required': 'False',
                                                   'placeholder': 'Частота подавителя'}),
            'deg_podavitelya': NumberInput(attrs={'class': 'form-control',
                                                  'placeholder': 'Номер подавителя (60, 120 ...)'}),
            'type_podavitelya': Select(attrs={'class': 'form-control', 'placeholder': 'Тип подавителя'}),
            'ip_podavitelya': TextInput(attrs={'class': 'form-control', 'placeholder': 'IP-адрес подавителя'}),
            'canal_podavitelya': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Канал подавителя'}),
            'usileniye_db': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Усиление, дб'}),
        }
