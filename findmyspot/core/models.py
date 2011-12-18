from django.contrib.gis.db import models
from settings import PROJECTION_SRID

class Hospital(models.Model):
    name = models.CharField(max_length=48)
    the_geom = models.PointField(srid=PROJECTION_SRID)
    description = models.TextField(blank=True)
    hours = models.CharField(max_length=100, blank=True)

    objects = models.GeoManager()

    class Meta:
        db_table = u'italia_points'
