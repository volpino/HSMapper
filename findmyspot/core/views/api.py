from django.http import HttpResponse
from vectorformats.Formats import Django, GeoJSON
from core.models import HaitiHospitals

def get_hospitals(request):
    qs = HaitiHospitals.objects.all()
    djf = Django.Django(geodjango="the_geom", properties=['id', 'name'])
    geoj = GeoJSON.GeoJSON()
    geojson_output = geoj.encode(djf.decode(qs))
    response = HttpResponse(mimetype="application/json")
    response.write(geojson_output)
    return response

def edit_hospital(request):
    result = "{success: false}"
    if request.method == 'POST':
        params = request.POST
        try:
            params_id = int(params["id"])
        except ValueError:
            params_id = -1
        current_obj = HaitiHospitals.objects.get(id=params_id)
        if current_obj:
            for key in params:
                if key != "id":
                    setattr(current_obj, key, params[key])
            current_obj.save()
            result = "{success: true}"
    response = HttpResponse(mimetype="application/json")
    response.write(result)
    return response

def add_hospital(request):
    result = "{success: false}"
    if request.method == 'POST':
        params = request.POST
        current_obj = HaitiHospitals()
        if current_obj:
            for key in params:
                if key != "id":
                    setattr(current_obj, key, params[key])
            current_obj.save()
            result = "{success: true}"
    response = HttpResponse(mimetype="application/json")
    response.write(result)
    return response

def delete_hospital(request):
    result = "{success: false}"
    if request.method == 'POST':
        params = request.POST
        try:
            params_id = int(params["id"])
        except ValueError:
            params_id = -1
        current_obj = HaitiHospitals.objects.get(id=params_id)
        current_obj.delete()
        result = "{success: true}"
    response = HttpResponse(mimetype="application/json")
    response.write(result)
    return response
