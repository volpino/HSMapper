# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from settings import PROJECTION_SRID
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.core.exceptions import ValidationError


class Pathology(models.Model):
    name = models.CharField(_("Name"), max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Pathology')
        verbose_name_plural = _('Pathologies')


class MedicalService(models.Model):
    name = models.CharField(_("Name"), max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Medical Service')
        verbose_name_plural = _('Medical Services')


class FacilityType(models.Model):
    name = models.CharField(_("Name"), max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Facility Type')
        verbose_name_plural = _('Facility Types')


class Facility(models.Model):
    name = models.CharField(_("Name"), max_length=255, null=True, blank=True)
    the_geom = models.PointField(_("Geometry"), srid=PROJECTION_SRID)
    description = models.TextField(_("Description"), null=True, blank=True)
    manager = models.ForeignKey('self', verbose_name=_("Depends on"),
                                null=True, blank=True)
    address = models.TextField(_("Address"), null=True, blank=True)
    phone = models.TextField(_("Phone"), null=True, blank=True)
    email = models.TextField(_("E-mail"), null=True, blank=True)
    facility_type = models.ForeignKey(FacilityType,
                                      verbose_name=_("Facility Type"),
                                      null=True, blank=True)
    pathologies = models.ManyToManyField(Pathology,
                                         verbose_name=_("Pathologies"),
                                         null=True, blank=True)
    services = models.ManyToManyField(MedicalService,
                                      verbose_name=_("Services"),
                                      null=True, blank=True)
    last_updated = models.DateField(_("Last update"), auto_now=True)
    updated_by = models.ForeignKey(User, verbose_name=_("Updated by"),
                                   null=True, blank=True)
    expiration = models.DateField(_("Expiration"), null=True, blank=True)
    open_24h = models.NullBooleanField(_("Open 24h"))

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name or ugettext("<No name>")

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
    facility = models.ForeignKey(Facility, verbose_name=_("Facility"))
    opening = models.TimeField(_("Opening time"), null=True, blank=True)
    closing = models.TimeField(_("Closing time"), null=True, blank=True)
    weekday = models.IntegerField(_("Weekday"), choices=WEEKDAY_CHOICES)
    index = models.IntegerField(_("Index"))

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
    facility = models.ForeignKey(Facility, verbose_name=_("Facility"))
    holiday_date = models.DateField(_("Date"), null=True, blank=True)
    closed = models.NullBooleanField(_("Closed all day"))
    opening = models.TimeField(_("Opening time"), null=True, blank=True)
    closing = models.TimeField(_("Closing time"), null=True, blank=True)

    class Meta:
        verbose_name = _('Special Day')
        verbose_name_plural = _('Special Days')
