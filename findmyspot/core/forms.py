from django.forms import ModelForm
from core.models import *

class HaitiHospitalsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(HaitiHospitalsForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.iteritems():
            self.fields[key].required = False
    class Meta:
        model = HaitiHospitals
        exclude = ["id"]
