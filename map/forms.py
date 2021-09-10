import django.forms
from django.forms import ModelForm, Select, ModelChoiceField, ModelMultipleChoiceField, CharField, IntegerField, \
    TextInput, SelectMultiple
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
    filtered_strizhes.widget = SelectMultiple(attrs={'id': 'choose_strizh', 'size': '4',
                                                     })

    class Meta:
        model = Strizh
        fields = ['filtered_strizhes']
        widgets = {
            'filtered_strizhes': SelectMultiple(attrs={'id': 'name', 'width': '300px',
                                                       'class': 'myfieldclass'}),
        }


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
                              label="Отсортировать",
                              widget=forms.Select(attrs={'onchange': 'submit();'}))

    class Meta:
        model = Point
        fields = ['field']


class TableOrderForm(ModelForm):
    zz = Point._meta.get_fields()
    # AllFields = tuple([(f.name, f.verbose_name) for f in Point._meta.get_fields()])
    AllFields = tuple([('', 'по возрастанию'), ('-', 'по убыванию')])
    order_sign = forms.ChoiceField(choices=AllFields, required=False,
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
    apem_toshow.widget = SelectMultiple(attrs={'size': 12, 'id': 'block1'
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
            'strizh_name': Select(attrs={'class': 'form-control', 'placeholder': 'Имя стрижа'}),
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
