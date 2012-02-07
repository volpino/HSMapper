from django.contrib.gis.geos.point import Point
from django.http import HttpResponse
from django.shortcuts import render_to_response
from vectorformats.Formats import Django, GeoJSON

from annoying.decorators import ajax_request

from core.models import Facility, FacilityType, Pathology, MedicalService
from core.forms import FacilityForm
import settings


def get_hospitals(request):
    qs = Facility.objects.exclude(the_geom=None)
    djf = Django.Django(geodjango="the_geom",
                        properties=['id', 'name', 'description', 'manager',
                                    'address', 'phone', 'email',
                                    'facility_type_id'])
    geoj = GeoJSON.GeoJSON()
    geojson_output = geoj.encode(djf.decode(qs))
    response = HttpResponse(mimetype="application/json")
    response.write(geojson_output)

    return response


@ajax_request
def edit_hospital(request, id_):
    if request.method == 'POST':
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
                if value:
                    current_data[key] = value

            obj = Facility(**current_data)

            if request.POST.has_key("pathologies[]"):
                p_data = request.POST.getlist("pathologies[]")
                obj.pathologies.clear()
                obj.save(force_update=True)
                for p in p_data:
                    try:
                        obj_p = Pathology.objects.get(name=p)
                        print "######", obj.pk, obj_p.pk
                        obj.pathologies.add(obj_p)
                    except Pathology.DoesNotExist:
                        obj.pathologies.create(name=p)

            if request.POST.has_key("services[]"):
                p_data = request.POST.getlist("services[]")
                obj.services.clear()
                for p in p_data:
                    try:
                        obj_p = MedicalService.objects.get(name=p)
                        obj.services.add(obj_p)
                    except MedicalService.DoesNotExist:
                        obj.services.create(name=p)

            obj.save(force_update=True)
            return {'success': True}
    return {'success': False}


@ajax_request
def edit_hospital_data(request, key):
    if key == "type":
        return dict([(k.id, k.name)
                     for k in FacilityType.objects.all()])
    if key == "manager":
        return dict([(k.id, k.name)
                     for k in Facility.objects.all()])
    elif key == "pathology":
        if request.GET.has_key(u'q'):
            results = []
            q = request.GET[u'q']
            if len(q) > 2:
                model_results = Pathology.objects.filter(name__icontains=q)
                for x in model_results:
                    results.append({"id": x.id, "name": x.name})
            return {"results": results}
    elif key == "service":
        if request.GET.has_key(u'q'):
            results = []
            q = request.GET[u'q']
            if len(q) > 2:
                model_results = MedicalService.objects.filter(name__icontains=q)
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
    return render_to_response('hospital_info.html', {'hospital': hospital})


@ajax_request
def add_hospital(request):
    if request.method == 'POST':
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


@ajax_request
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
