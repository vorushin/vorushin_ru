# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Tag'
        db.create_table('blog_tag', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('blog', ['Tag'])

        # Adding model 'Entry'
        db.create_table('blog_entry', (
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('text_markdown', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 3, 8, 16, 4, 47, 353586))),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('blog', ['Entry'])

        # Adding M2M table for field tags on 'Entry'
        db.create_table('blog_entry_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm['blog.entry'], null=False)),
            ('tag', models.ForeignKey(orm['blog.tag'], null=False))
        ))
        db.create_unique('blog_entry_tags', ['entry_id', 'tag_id'])

        # Adding model 'Link'
        db.create_table('blog_link', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('text_markdown', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 3, 8, 16, 4, 47, 354589))),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('blog', ['Link'])

        # Adding M2M table for field tags on 'Link'
        db.create_table('blog_link_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('link', models.ForeignKey(orm['blog.link'], null=False)),
            ('tag', models.ForeignKey(orm['blog.tag'], null=False))
        ))
        db.create_unique('blog_link_tags', ['link_id', 'tag_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Tag'
        db.delete_table('blog_tag')

        # Deleting model 'Entry'
        db.delete_table('blog_entry')

        # Removing M2M table for field tags on 'Entry'
        db.delete_table('blog_entry_tags')

        # Deleting model 'Link'
        db.delete_table('blog_link')

        # Removing M2M table for field tags on 'Link'
        db.delete_table('blog_link_tags')
    
    
    models = {
        'blog.entry': {
            'Meta': {'object_name': 'Entry'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 3, 8, 16, 4, 47, 357480)'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['blog.Tag']", 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'text_markdown': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'blog.link': {
            'Meta': {'object_name': 'Link'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 3, 8, 16, 4, 47, 358428)'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['blog.Tag']", 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'text_markdown': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'blog.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['blog']
