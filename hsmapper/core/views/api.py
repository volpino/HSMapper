from django.contrib.gis.geos.point import Point
from django.http import HttpResponse
from django.shortcuts import render_to_response
from vectorformats.Formats import Django, GeoJSON

from ajaxutils.decorators import ajax

from hsmapper import settings
from core.models import Facility, FacilityType, Pathology, MedicalService, \
                        OpeningTime, WEEKDAY_CHOICES
from core.forms import make_facility_form


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
    if request.method == 'POST':
        FacilityForm = make_facility_form()
        form = FacilityForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                current_obj = Facility.objects.get(id=id_)
            except Facility.DoesNotExist:
                return {'success': False, 'error': 'Not found'}

            current_data = dict([(k.name, getattr(current_obj, k.name))
                                 for k in current_obj._meta.fields])

            for key, value in data.items():
                if key.startswith("optime_") and value:
                    key = key.split("_")
                    print key, value
                    try:
                        weekday = int(key[1])
                        rel_index = int(key[2])
                        type_ = int(key[3])
                    except (ValueError, TypeError, IndexError):
                        pass
                    else:
                        op_times = current_obj.openingtime_set.\
                                   filter(weekday=weekday).order_by("id")

                        if len(op_times) < 2:
                            for _ in range(2):  # build openingtimes
                                op = OpeningTime(
                                    facility=current_obj,
                                    weekday=weekday
                                )
                                op.save()

                        op_times = current_obj.openingtime_set.\
                                   filter(weekday=weekday).order_by("id")
                        op = op_times[rel_index]
                        if type_ == 0:
                            op.opening = value
                        elif type_ == 1:
                            op.closing = value
                        else:
                            raise ValueError
                        op.save()

                elif key == "manager" or value:
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
    return {'success': False}


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
                               'weekdays': WEEKDAY_CHOICES})


@ajax(login_required=True, require_POST=True)
def add_hospital(request):
    if request.method == 'POST':
        FacilityForm = make_facility_form()
        form = FacilityForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            lat = data['lat']
            lon = data['lon']
            if not (lat and lon):
                return {'success': False, 'error': 'Lat or long are empty'}

            del data['lat'], data['lon']
            data['the_geom'] = Point(lon, lat, srid=settings.DISPLAY_SRID)

            obj = Facility.objects.create(**data)
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
