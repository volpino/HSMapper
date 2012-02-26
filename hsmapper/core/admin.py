"""
Admin module for hsmapper core app
"""

from django.contrib.gis import admin
import reversion
from core.models import Pathology, MedicalService, FacilityType, Facility, \
                    OpeningTime, SpecialDay


class FacilityAdmin(reversion.VersionAdmin, admin.GeoModelAdmin):
    """ Wrapper class for django-reversion and geodjango """
    list_display = ('name', 'address', 'facility_type')


admin.site.register(Pathology)
admin.site.register(MedicalService)
admin.site.register(FacilityType)
admin.site.register(Facility, FacilityAdmin)
admin.site.register(OpeningTime)
admin.site.register(SpecialDay)
