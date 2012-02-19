# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from settings import PROJECTION_SRID
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


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
    open_24h = models.NullBooleanField()

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name or unicode(_("<No name>"))

    class Meta:
        verbose_name = _('Facility')
        verbose_name_plural = _('Facilities')


WEEKDAY_CHOICES = ((0, _("Monday")),
                   (1, _("Tuesday")),
                   (2, _("Wednesday")),
                   (3, _("Thursday")),
                   (4, _("Friday")),
                   (5, _("Saturday")),
                   (6, _("Sunday")))


class OpeningTime(models.Model):
    facility = models.ForeignKey(Facility)
    opening = models.TimeField(null=True, blank=True)
    closing = models.TimeField(null=True, blank=True)
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    index = models.IntegerField()

    def __unicode__(self):
        return u"[%d] %s: %s-%s" % (
            self.facility.pk, WEEKDAY_CHOICES[self.weekday][1],
            self.opening, self.closing
        )

    def save(self, *args, **kwargs):
        if (self.opening and self.closing) and self.opening > self.closing:
            raise ValidationError(
                "Opening time should be before closing time."
            )
        super(OpeningTime, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Opening Time')
        verbose_name_plural = _('Opening Times')
        unique_together = ("facility", "weekday", "index")


class SpecialDay(models.Model):
    facility = models.ForeignKey(Facility)
    holiday_date = models.DateField(null=True, blank=True)
    closed = models.NullBooleanField()
    opening = models.TimeField(null=True, blank=True)
    closing = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Special Day')
        verbose_name_plural = _('Special Days')
