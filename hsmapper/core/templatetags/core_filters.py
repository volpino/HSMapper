from datetime import datetime
from django import template

register = template.Library()

@register.filter
def in_the_past(date):
    return date < datetime.now()
