from django.forms import ModelForm, Select, ModelChoiceField, ModelMultipleChoiceField, CharField

# from .models import MyModel, MyStrizh
from geo.models import Strizh, Point, DroneJournal
from django.forms import widgets


class StrizhForm(ModelForm):
    chosen_strizh = ModelChoiceField(queryset=Strizh.objects.all(), empty_label="Выберите стрижа",
                                     required=False, to_field_name="name",
                                     label="")

    # print(chosen_strizh)
    class Meta:
        model = Strizh
        fields = ['chosen_strizh']
        widgets = {
            'chosen_strizh': Select(attrs={'id': 'name'}),
        }


class StrizhFilterForm(ModelForm):
    filtered_strizhes = ModelMultipleChoiceField(queryset=Strizh.objects.all(),
                                                 required=False, to_field_name="name",
                                                 label="" )
    # widget = widgets.SelectMultiple(attrs={'size': 10})
    class Meta:
        model = Strizh
        fields = ['filtered_strizhes']

        widgets = {
            'filtered_strizhes': Select(attrs={'id': 'name', 'width': '300px'}),

        }


class DroneFilterForm(ModelForm):
    drone_toshow = ModelMultipleChoiceField(queryset=Point.objects.all().order_by('-detection_time'),
                                            required=False, to_field_name="pk",
                                            label="")
    class Meta:
        model = Point
        # model = MyStrizh
        fields = ['drone_toshow']
