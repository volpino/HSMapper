from django import forms
from django.forms import Form
from core.models import Facility, FacilityType

#import jsonfield


class FacilityForm(Form):
    """Form for editing facilities properties
    """
    # ModelForm is not used because required must be False everywhere
    name = forms.CharField(max_length=255,
                           required=False)
    description = forms.CharField(widget=forms.TextInput(),
                                  required=False)
    manager = forms.ModelChoiceField(queryset=Facility.objects.all(),
                                     required=False)
    address = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    email = forms.CharField(required=False)
    facility_type = forms.ModelChoiceField(queryset=FacilityType.objects.all(),
                                           required=False)
    expiration = forms.DateField(required=False)

    lat = forms.FloatField(widget=forms.HiddenInput(), required=False)
    lon = forms.FloatField(widget=forms.HiddenInput(), required=False)
    #the_geom = jsonfield.JSONField(blank=True)
