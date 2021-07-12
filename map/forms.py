from django.forms import ModelForm, Select, ModelChoiceField

# from .models import MyModel, MyStrizh
from geo.models import Strizh

# class MyModelForm(ModelForm):
#     class Meta:
#         model = MyModel
#         fields = ['color']


class StrizhForm(ModelForm):
    chosen_strizh = ModelChoiceField(queryset=Strizh.objects.all(), empty_label="Выберите стрижа",
                                     required=False, help_text="Выбор стрижа", to_field_name="name")
    print(chosen_strizh)
    class Meta:
        model = Strizh
        # model = MyStrizh
        fields = ['name']

        widgets = {
            'name': Select(attrs={'id': 'name'}),
        }
