# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Pathology'
        db.create_table(u'pathology', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('core', ['Pathology'])

        # Adding model 'MedicalService'
        db.create_table(u'medicalservice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('core', ['MedicalService'])

        # Adding model 'FacilityType'
        db.create_table(u'facilitytype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('core', ['FacilityType'])

        # Adding model 'Facility'
        db.create_table(u'facility', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('the_geom', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=23032)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('manager', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('facility_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.FacilityType'], null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('expiration', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Facility'])

        # Adding M2M table for field pathologies on 'Facility'
        db.create_table(u'facility_pathologies', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('facility', models.ForeignKey(orm['core.facility'], null=False)),
            ('pathology', models.ForeignKey(orm['core.pathology'], null=False))
        ))
        db.create_unique(u'facility_pathologies', ['facility_id', 'pathology_id'])

        # Adding M2M table for field services on 'Facility'
        db.create_table(u'facility_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('facility', models.ForeignKey(orm['core.facility'], null=False)),
            ('medicalservice', models.ForeignKey(orm['core.medicalservice'], null=False))
        ))
        db.create_unique(u'facility_services', ['facility_id', 'medicalservice_id'])

        # Adding model 'OpeningTime'
        db.create_table(u'openingtime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('facility', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Facility'])),
            ('opening', self.gf('django.db.models.fields.TimeField')()),
            ('closing', self.gf('django.db.models.fields.TimeField')()),
            ('weekday', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('core', ['OpeningTime'])

        # Adding model 'SpecialDays'
        db.create_table(u'specialdays', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('facility', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Facility'])),
            ('holiday_date', self.gf('django.db.models.fields.DateField')()),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('opening', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('closing', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['SpecialDays'])


    def backwards(self, orm):
        
        # Deleting model 'Pathology'
        db.delete_table(u'pathology')

        # Deleting model 'MedicalService'
        db.delete_table(u'medicalservice')

        # Deleting model 'FacilityType'
        db.delete_table(u'facilitytype')

        # Deleting model 'Facility'
        db.delete_table(u'facility')

        # Removing M2M table for field pathologies on 'Facility'
        db.delete_table('facility_pathologies')

        # Removing M2M table for field services on 'Facility'
        db.delete_table('facility_services')

        # Deleting model 'OpeningTime'
        db.delete_table(u'openingtime')

        # Deleting model 'SpecialDays'
        db.delete_table(u'specialdays')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.facility': {
            'Meta': {'object_name': 'Facility', 'db_table': "u'facility'"},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'expiration': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'facility_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.FacilityType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'manager': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pathologies': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['core.Pathology']", 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['core.MedicalService']", 'null': 'True', 'blank': 'True'}),
            'the_geom': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '23032'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'core.facilitytype': {
            'Meta': {'object_name': 'FacilityType', 'db_table': "u'facilitytype'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'core.medicalservice': {
            'Meta': {'object_name': 'MedicalService', 'db_table': "u'medicalservice'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'core.openingtime': {
            'Meta': {'object_name': 'OpeningTime', 'db_table': "u'openingtime'"},
            'closing': ('django.db.models.fields.TimeField', [], {}),
            'facility': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Facility']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'opening': ('django.db.models.fields.TimeField', [], {}),
            'weekday': ('django.db.models.fields.IntegerField', [], {})
        },
        'core.pathology': {
            'Meta': {'object_name': 'Pathology', 'db_table': "u'pathology'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'core.specialdays': {
            'Meta': {'object_name': 'SpecialDays', 'db_table': "u'specialdays'"},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'closing': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'facility': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Facility']"}),
            'holiday_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'opening': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['core']
