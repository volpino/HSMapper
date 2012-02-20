import datetime
from django import template

register = template.Library()

@register.filter
def is_still_valid(date):
    if not date:
        return False
    else:
        return datetime.date.today() < date

@register.filter
def get_item(list_, index):
    try:
        return [x for x in list_][int(index)]
    except (ValueError, TypeError, IndexError):
        return u""

@register.filter
def filter_wd(queryset, weekday):
    return queryset.filter(weekday=weekday[0]).order_by("opening")
