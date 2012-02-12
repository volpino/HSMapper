# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
#from django.db import models
from django.contrib.auth.models import User
from settings import PROJECTION_SRID
from django.utils.translation import ugettext_lazy as _


class Pathology(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Pathology')
        verbose_name_plural = _('Pathologies')


class MedicalService(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Medical Service')
        verbose_name_plural = _('Medical Services')


class FacilityType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Facility Type')
        verbose_name_plural = _('Facility Types')


class Facility(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    the_geom = models.PointField(srid=PROJECTION_SRID)
    description = models.TextField(null=True, blank=True)
    manager = models.ForeignKey('self', null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    facility_type = models.ForeignKey(FacilityType, null=True, blank=True)
    pathologies = models.ManyToManyField(Pathology, null=True, blank=True)
    services = models.ManyToManyField(MedicalService, null=True, blank=True)
    last_updated = models.DateField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True, blank=True)
    expiration = models.DateField(null=True, blank=True)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name or unicode(_("<No name>"))

    class Meta:
        verbose_name = _('Facility')
        verbose_name_plural = _('Facilities')


WEEKDAY_CHOICES = ((1, _("Monday")),
                   (2, _("Tuesday")),
                   (3, _("Wednesday")),
                   (4, _("Thursday")),
                   (5, _("Friday")),
                   (6, _("Saturday")),
                   (7, _("Sunday")))


class OpeningTime(models.Model):
    facility = models.ForeignKey(Facility)
    opening = models.TimeField()
    closing = models.TimeField()
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)

    class Meta:
        verbose_name = _('Opening Time')
        verbose_name_plural = _('Opening Times')


class SpecialDay(models.Model):
    facility = models.ForeignKey(Facility)
    holiday_date = models.DateField()
    closed = models.BooleanField()
    opening = models.TimeField(null=True, blank=True)
    closing = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Special Day')
        verbose_name_plural = _('Special Days')
