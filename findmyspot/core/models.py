from django.contrib.gis.db import models

class HaitiPoints(models.Model):
    gid = models.IntegerField(primary_key=True)
    osm_id = models.DecimalField(max_digits=11, decimal_places=0)
    timestamp = models.CharField(max_length=20)
    name = models.CharField(max_length=48)
    type = models.CharField(max_length=16)
    the_geom = models.PointField(srid=900913)
    class Meta:
        db_table = u'haiti_points'

class HaitiHospitals(models.Model):
    name = models.CharField(max_length=48)
    the_geom = models.PointField(srid=900913)
    description = models.TextField(blank=True)
    hours = models.CharField(max_length=100, blank=True)

    objects = models.GeoManager()

    class Meta:
        db_table = u'haiti_hospitals'

class HaitiRoads(models.Model):
    name = models.CharField(max_length=48)
    type = models.CharField(max_length=48)
    ref = models.CharField(max_length=16)
    oneway = models.SmallIntegerField()
    bridge = models.SmallIntegerField()
    maxspeed = models.SmallIntegerField()
    weight = models.SmallIntegerField()
    the_geom = models.TextField()
    class Meta:
        db_table = u'haiti_roads'
