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
