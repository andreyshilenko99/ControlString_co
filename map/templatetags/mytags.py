from django import template
register = template.Library()

@register.filter
def division(value, div):
    return round((value / div), 2)

