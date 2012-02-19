from vectorformats.Formats import Django, GeoJSON
from ajaxutils.decorators import ajax

from django.contrib.gis.geos.point import Point
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.exceptions import ValidationError

from hsmapper import settings
from core.models import Facility, FacilityType, Pathology, MedicalService, \
                        OpeningTime, WEEKDAY_CHOICES
from core.forms import FacilityForm


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
    if form.is_valid():
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

        if weekday >= 0 and optime >= 0:
            try:
                op_time = current_obj.openingtime_set.get(
                    weekday=weekday,
                    index=optime
                )
            except OpeningTime.DoesNotExist:
                op = OpeningTime(
                    facility=current_obj,
                    weekday=weekday,
                    opening=(opening or None),
                    closing=(closing or None),
                    index=optime
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

        current_data = dict([(k.name, getattr(current_obj, k.name))
                             for k in current_obj._meta.fields])

        for key, value in data.items():
            if key == "manager" or value:
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

        obj.save(force_update=True)
        return {'success': True}


@ajax(login_required=True)
def edit_hospital_data(request, key):
    if key == "type":
        return dict([(k.id, k.name)
                     for k in FacilityType.objects.all()])

    if key == "manager":
        return dict([(k.id, str(k))
                     for k in Facility.objects.all()] + [("", "--------")])

    elif key == "pathology":
        if "q" in request.GET:
            results = []
            q = request.GET[u'q']
            if len(q) > 2:
                model_results = Pathology.objects.filter(name__icontains=q)
                for x in model_results:
                    results.append({"id": x.id, "name": x.name})
            return {"results": results}

    elif key == "service":
        if "q" in request.GET:
            results = []
            q = request.GET[u'q']

            if len(q) > 2:
                model_results = MedicalService.objects.filter(
                                    name__icontains=q
                                )
                for x in model_results:
                    results.append({"id": x.id, "name": x.name})
            return {"results": results}

    return {}


def info_hospital(request, id_):
    hospital = None
    params_id = int(id_)
    try:
        hospital = Facility.objects.get(id=params_id)
    except Facility.DoesNotExist:
        pass
    return render_to_response('hospital_info.html',
                              {'hospital': hospital,
                               'weekdays': WEEKDAY_CHOICES},
                              context_instance=RequestContext(request))


@ajax(login_required=True, require_POST=True)
def add_hospital(request):
    if request.method == 'POST':
        form = FacilityForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            lat = data['lat']
            lon = data['lon']
            if not (lat and lon):
                return {'success': False, 'error': 'Lat or long are empty'}

            the_geom = Point(lon, lat, srid=settings.DISPLAY_SRID)

            obj = Facility.objects.create(the_geom=the_geom)
            return {'success': True, 'id': obj.pk}
    return {'success': False}


@ajax(login_required=True, require_POST=True)
def delete_hospital(request, id_):
    if request.method == 'POST':
        params_id = int(id_)
        try:
            hospital = Facility.objects.get(id=params_id)
            hospital.delete()
        except Facility.DoesNotExist:
            return {'success': False}
        return {'success': True}
    return {'success': False}
