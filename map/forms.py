from django.forms import ModelForm, Select, ModelChoiceField, ModelMultipleChoiceField, CharField

# from .models import MyModel, MyStrizh
from geo.models import Strizh, Point, DroneJournal


# class MyModelForm(ModelForm):
#     class Meta:
#         model = MyModel
#         fields = ['color']


class StrizhForm(ModelForm):
    chosen_strizh = ModelChoiceField(queryset=Strizh.objects.all(), empty_label="Выберите стрижа",
                                     required=False, to_field_name="name",
                                     label="")
    # print(chosen_strizh)
    class Meta:
        model = Strizh
        # model = MyStrizh
        fields = ['chosen_strizh']
        widgets = {
            'chosen_strizh': Select(attrs={'id': 'name'}),
            # 'chosen_strizh': ModelChoiceField(queryset=Strizh.objects.all(), empty_label="Выберите стрижа",
            #                                  required=False, help_text="Выбор стрижа", to_field_name="name")
        }


class StrizhFilterForm(ModelForm):
    filtered_strizhes = ModelMultipleChoiceField(queryset=Strizh.objects.all(),
                                     required=False, to_field_name="name",
                                     label="")
    # print(chosen_strizh)
    class Meta:
        model = Strizh
        # model = MyStrizh
        fields = ['filtered_strizhes']

        widgets = {
            'filtered_strizhes': Select(attrs={'id': 'name'}),
            # 'chosen_strizh': ModelChoiceField(queryset=Strizh.objects.all(), empty_label="Выберите стрижа",
            #                                  required=False, help_text="Выбор стрижа", to_field_name="name")
        }



class DroneFilterForm(ModelForm):
    drone_toshow = ModelMultipleChoiceField(queryset=Point.objects.all().order_by('-detection_time'),
                                     required=False, to_field_name="pk",
                                     label="")
    # print(chosen_strizh)
    class Meta:
        model = Point
        # model = MyStrizh
        fields = ['drone_toshow']

        # widgets = {
        #     'drone_toshow': Select(attrs={'id': 'detection_time'}),
        #     # 'chosen_strizh': ModelChoiceField(queryset=Strizh.objects.all(), empty_label="Выберите стрижа",
        #     #                                  required=False, help_text="Выбор стрижа", to_field_name="name")
        # }