from django.forms import ModelForm, Select, ModelChoiceField, ModelMultipleChoiceField, CharField

# from .models import MyModel, MyStrizh
from geo.models import Strizh, Point, DroneJournal, StrizhJournal
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
                                                 label="")

    # widget = widgets.SelectMultiple(attrs={'size': 10})
    class Meta:
        model = Strizh
        fields = ['filtered_strizhes']

        widgets = {
            'filtered_strizhes': Select(attrs={'id': 'name', 'width': '300px'}),

        }


class DroneFilterForm(ModelForm):
    names_arr = []
    AllDrones = Point.objects.all().order_by('-detection_time')

    # if len(AllDrones) != 0:
    #     filter_values = StrizhJournal.objects.all().order_by('-pk')
    #     names_arr = filter_values[0].filtered_strizhes.split(';; ')
    #
    #     drone_toshow = ModelMultipleChoiceField(queryset=AllDrones.filter(strig_name__in=names_arr),
    #                                             required=False, to_field_name="pk",
    #                                             label="")
    # else:
    #     # needed_drones = names_arr.filtered_strizhes

    drone_toshow = ModelMultipleChoiceField(queryset=AllDrones,
                                            required=False, to_field_name="pk",
                                            label="")


    class Meta:
        model = Point
        # model = MyStrizh
        fields = ['drone_toshow']
