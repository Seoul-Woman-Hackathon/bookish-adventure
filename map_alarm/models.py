# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models



class Accidents(models.Model):
    idaccidents = models.AutoField(primary_key=True)
    region = models.PolygonField(blank=True, null=True)
    name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'accidents'


class Lights(models.Model):
    idlights = models.AutoField(primary_key=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    accidents_idaccidents = models.ForeignKey(Accidents, models.DO_NOTHING, db_column='accidents_idaccidents')

    class Meta:
        managed = False
        db_table = 'lights'



class Guardian(models.Model):
    idguardian = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    phonenum = models.CharField(max_length=45, blank=True, null=True)
    user_iduser = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'guardian'
