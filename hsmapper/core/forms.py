""" Forms for hsmapper core app """

from django import forms
from core.models import Facility, FacilityType, WEEKDAY_CHOICES


class FacilityForm(forms.Form):
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
    expiration = forms.DateField(required=False, input_formats=['%d/%m/%Y'])

    lat = forms.FloatField(widget=forms.HiddenInput(), required=False)
    lon = forms.FloatField(widget=forms.HiddenInput(), required=False)

    # timetable fields
    weekday = forms.ChoiceField(choices=WEEKDAY_CHOICES, required=False)
    optime = forms.IntegerField(required=False) # index of the opening time
    opening = forms.TimeField(required=False)
    closing = forms.TimeField(required=False)

    open_24h = forms.BooleanField(required=False)
