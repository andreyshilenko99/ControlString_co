from django import template
register = template.Library()

@register.filter
def division(value, div):
    return round((value / div), 2)


@register.filter(name='getkey')
def getkey(value, arg):
    return value[arg]

