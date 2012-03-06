"""
Views for hsmapper.core
"""

from vectorformats.Formats import Django, GeoJSON
from ajaxutils.decorators import ajax

from django.contrib.gis.geos.point import Point
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _

from hsmapper import settings
from core.models import Facility, FacilityType, Pathology, MedicalService, \
                        WEEKDAY_CHOICES
from core.forms import FacilityForm
from core.helpers import lookup_query, timetable_filler, \
                         remove_dangling_objects


def get_hospitals(request):
    qs = Facility.objects.exclude(the_geom=None)
    djf = Django.Django(geodjango="the_geom",
                        properties=['id', 'name', 'description', 'manager_id',
                                    'address', 'phone', 'email',
                                    'facility_type_id'])
    geoj = GeoJSON.GeoJSON()
    geojson_output = geoj.encode(djf.decode(qs))
    response = HttpResponse(mimetype="application/json")
    response.write(geojson_output)

    return response


@ajax(login_required=True, require_POST=True)
def edit_hospital(request, id_):
    form = FacilityForm(request.POST)
    if form.is_valid() and request.POST:
        try:
            current_obj = Facility.objects.get(id=id_)
        except Facility.DoesNotExist:
            return {'success': False, 'error': 'Not found'}

        data = form.cleaned_data

        # timetable data
        weekday = data["weekday"]
        optime = data["optime"]
        opening = data["opening"]
        closing = data["closing"]
        del data["weekday"], data["optime"], data["opening"], \
            data["closing"]

        res = timetable_filler(current_obj, weekday, optime, opening, closing)
        if res:
            return res

        current_data = dict([(k.name, getattr(current_obj, k.name))
                             for k in current_obj._meta.fields])

        for key, value in data.items():
            if key in request.POST:
                current_data[key] = value

        obj = Facility(**current_data)
        obj.updated_by = request.user

        if "pathologies[]" in request.POST:
            p_data = request.POST.getlist("pathologies[]")
            obj.pathologies.clear()
            obj.save(force_update=True)
            for p in p_data:
                if p:
                    try:
                        obj_p = Pathology.objects.get(name=p)
                        obj.pathologies.add(obj_p)
                    except Pathology.DoesNotExist:
                        obj.pathologies.create(name=p)
            # TODO: is it good or bad?
            # TODO: This should be an async task
            remove_dangling_objects(Pathology)

        if "services[]" in request.POST:
            p_data = request.POST.getlist("services[]")
            obj.services.clear()
            obj.save(force_update=True)
            for p in p_data:
                if p:
                    try:
                        obj_p = MedicalService.objects.get(name=p)
                        obj.services.add(obj_p)
                    except MedicalService.DoesNotExist:
                        obj.services.create(name=p)
            # TODO: is it good or bad?
            # TODO: This should be an async task
            remove_dangling_objects(MedicalService)

        obj.save(force_update=True)
        return {'success': True}
    return {'success': False, 'error': form.errors}


@ajax(login_required=True)
def edit_hospital_data(request, key):
    qry = request.GET.get("q", None)

    if key == "type":
        return dict([(k.pk, k.name)
                     for k in FacilityType.objects.all()])

    if key == "manager":
        return dict([(k.pk, str(k)) for k in Facility.objects.all()] + \
                    [("", _("None"))])

    elif key == "pathology" and qry:
            return lookup_query(qry, Pathology)

    elif key == "service" and qry:
            return lookup_query(qry, MedicalService)

    return {}


def info_hospital(request, id_):
    hospital = None
    params_id = int(id_)
    try:
        hospital = Facility.objects.get(id=params_id)
    except Facility.DoesNotExist:
        pass
    return render_to_response(
        'hospital_info.html',
        {'hospital': hospital, 'weekdays': WEEKDAY_CHOICES},
        context_instance=RequestContext(request)
    )


@ajax(login_required=True, require_POST=True)
def add_hospital(request):
    form = FacilityForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data

        lat = data['lat']
        lon = data['lon']
        if not (lat and lon):
            return {'success': False, 'error': 'lat or lon are empty'}

        the_geom = Point(lon, lat, srid=settings.DISPLAY_SRID)

        obj = Facility.objects.create(the_geom=the_geom)
        return {'success': True, 'id': obj.pk}


@ajax(login_required=True, require_POST=True)
def delete_hospital(request, id_):
    params_id = int(id_)
    try:
        hospital = Facility.objects.get(id=params_id)
        hospital.delete()
    except Facility.DoesNotExist:
        return {'success': False}
    return {'success': True}
