from django import template
import re
from django.utils.safestring import mark_safe
import json

register = template.Library()


@register.filter(name='division3')
def division3(value, div):
    return round((value / div), 3)


# @register.filter(name='division0')
# def division0(value, div):
#     return round((value / div), 0)


@register.filter(name='getkey')
def getkey(value, arg):
    return value[arg]


@register.filter()
def get_int(value):
    res = int(re.search(r'\d+', value).group())
    return res


@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))
