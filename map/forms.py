from django.forms import ModelForm, Select, ModelChoiceField, ModelMultipleChoiceField

# from .models import MyModel, MyStrizh
from geo.models import Strizh

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