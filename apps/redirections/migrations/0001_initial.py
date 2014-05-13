# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Redirection'
        db.create_table('redirections_redirection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('redirect_to', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('redirections', ['Redirection'])


    def backwards(self, orm):
        
        # Deleting model 'Redirection'
        db.delete_table('redirections_redirection')


    models = {
        'redirections.redirection': {
            'Meta': {'object_name': 'Redirection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'redirect_to': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['redirections']
