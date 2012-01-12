# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
from settings import PROJECTION_SRID


class Pathology(models.Model):
    name = models.CharField(max_length=255)


class MedicalService(models.Model):
    name = models.CharField(max_length=255)


class FacilityType(models.Model):
    name = models.CharField(max_length=255)


class Facility(models.Model):
    name = models.CharField(max_length=255)
    the_geom = models.PointField(srid=PROJECTION_SRID)
    description = models.TextField(null=True, blank=True)
    manager = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    facility_type = models.ForeignKey(FacilityType, null=True, blank=True)
    pathologies = models.ManyToManyField(Pathology, null=True, blank=True)
    services = models.ManyToManyField(MedicalService, null=True, blank=True)

    objects = models.GeoManager()

    class Meta:
        #db_table = u'italia_points'
        pass


WEEKDAY_CHOICES = ((1, u"Lunedì"),
                   (2, u"Martedì"),
                   (3, u"Mercoledì"),
                   (4, u"Giovedì"),
                   (5, u"Venerdì"),
                   (6, u"Sabato"),
                   (7, u"Domenica"))


class OpeningTime(models.Model):
    facility = models.ForeignKey(Facility)
    opening = models.TimeField()
    closing = models.TimeField()
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)


class SpecialDays(models.Model):
    facility = models.ForeignKey(Facility)
    holiday_date = models.DateField()
    closed = models.BooleanField()
    opening = models.TimeField(null=True, blank=True)
    closing = models.TimeField(null=True, blank=True)
