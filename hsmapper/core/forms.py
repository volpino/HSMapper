""" Forms for hsmapper core app """

from django import forms
from core.models import Facility, FacilityType, WEEKDAY_CHOICES

#import jsonfield

def make_facility_form():
    """Form for editing facilities properties
    """

    # ModelForm is not used because required must be False everywhere
    fields = {"name": forms.CharField(max_length=255, required=False),
              "description": forms.CharField(widget=forms.TextInput(),
                                             required=False),
              "manager": forms.ModelChoiceField(
                             queryset=Facility.objects.all(),
                             required=False
                         ),
              "address": forms.CharField(required=False),
              "phone": forms.CharField(required=False),
              "email": forms.CharField(required=False),
              "facility_type": forms.ModelChoiceField(
                                   queryset=FacilityType.objects.all(),
                                   required=False
                               ),
              "expiration": forms.DateField(
                                required=False,
                                input_formats=['%d/%m/%Y']
                            ),

              "lat": forms.FloatField(widget=forms.HiddenInput(),
                                      required=False),
              "lon": forms.FloatField(widget=forms.HiddenInput(),
                                      required=False)}
    weekdays = {}
    for wd in WEEKDAY_CHOICES:
        for i in range(2):
            for j in range(2):
                id_ = "optime_%d_%d_%d" % (wd[0], i, j)
                weekdays[id_] = forms.TimeField(required=False)
    fields.update(weekdays)
    #the_geom = jsonfield.JSONField(blank=True)
    return type('FacilityForm', (forms.BaseForm,), { 'base_fields': fields })
