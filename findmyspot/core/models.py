from django.contrib.gis.db import models

class HaitiPoints(models.Model):
    gid = models.IntegerField(primary_key=True)
    osm_id = models.DecimalField(max_digits=11, decimal_places=0)
    timestamp = models.CharField(max_length=20)
    name = models.CharField(max_length=48)
    type = models.CharField(max_length=16)
    the_geom = models.PointField() # This field type is a guess.
    class Meta:
        db_table = u'haiti_points'

class HaitiHospitals(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=48)
    the_geom = models.PointField() # This field type is a guess.
    class Meta:
        db_table = u'haiti_hospitals'

class HaitiRoads(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=48)
    type = models.CharField(max_length=48)
    ref = models.CharField(max_length=16)
    oneway = models.SmallIntegerField()
    bridge = models.SmallIntegerField()
    maxspeed = models.SmallIntegerField()
    weight = models.SmallIntegerField()
    the_geom = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'haiti_roads'
