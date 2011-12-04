from django import forms
from django.forms import Form

import jsonfield


class HaitiHospitalsForm(Form):
    name = forms.CharField(max_length=48, required=False)
    the_geom = jsonfield.JSONField(blank=True)
