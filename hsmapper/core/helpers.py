"""
Helpers for hsmapper core app
"""

from django.core.exceptions import ValidationError
from core.models import OpeningTime


def lookup_query(qry, model, attrs=None):
    results = []

    if attrs is None:
        attrs = ["id", "name"]

    if len(qry) > 2:
        model_results = model.objects.filter(name__icontains=qry)

        for obj in model_results:
            results.append(dict([(key, getattr(obj, key)) for key in attrs]))

    return {"results": results}


def timetable_filler(facility, weekday, index, opening, closing):
    if weekday >= 0 and index >= 0:
        try:
            op_time = facility.openingtime_set.get(
                weekday=weekday,
                index=index
            )
        except OpeningTime.DoesNotExist:
            op = OpeningTime(
                facility=facility,
                weekday=weekday,
                opening=(opening or None),
                closing=(closing or None),
                index=index
            )
            try:
                op.save()
            except ValidationError, exc:
                return {"success": False, "error": "%r" % exc}
        else:
            if opening is None and closing is None:
                op_time.delete()
            else:
                op_time.opening = opening or op_time.opening
                op_time.closing = closing or op_time.closing
                try:
                    op_time.save(force_update=True)
                except ValidationError, exc:
                    return {"success": False, "error": "%r" % exc}
