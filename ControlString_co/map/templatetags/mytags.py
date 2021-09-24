from django import template
import re
from django.utils.safestring import mark_safe
import json

register = template.Library()


@register.filter
def division(value, div):
    return round((value / div), 2)


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
