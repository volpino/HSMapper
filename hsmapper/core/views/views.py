from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.conf import settings


def home(request):
    return render_to_response(
        "home.html",
        {"server_ip": settings.SERVER_IP,
         "geoserver_port": settings.GEOSERVER_PORT,
         "srid": settings.PROJECTION_SRID},
        context_instance=RequestContext(request)
    )
