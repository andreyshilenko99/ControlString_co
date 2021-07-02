from django.forms import ModelForm

from .models import MyModel, MyStrizh
from geo.models import Strizh

class MyModelForm(ModelForm):
    class Meta:
        model = MyModel
        fields = ['color']


class StrizhForm(ModelForm):
    class Meta:
        # model = Strizh
        model = MyStrizh
        # fields = ['name']
        fields = ['choice_strizh']
        placeholder = "hui"
