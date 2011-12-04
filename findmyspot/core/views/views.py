from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.conf import settings


def home(request):
    SERVER_IP = settings.SERVER_IP
    return render_to_response("home.html", locals(),
        context_instance=RequestContext(request)
    )
