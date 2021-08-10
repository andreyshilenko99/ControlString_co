from django import template
import re

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
