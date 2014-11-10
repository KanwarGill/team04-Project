from django.db import models

# Create your models here.

class Article(models.Model):
    url = models.URLField(max_length=200)
    title = models.CharField(max_length=200)
    date_added = models.DateField('Date Added')
    date_published = models.DateField('Date Published')
    influence = models.IntegerField(default=0)

    def __unicode__(self):
        if len(self.title) >= 30:
            return self.title[:27] + '...'
        return self.title

class Author(models.Model):
    article = models.ForeignKey(Article)
    author = models.CharField(max_length=200)

    def __unicode__(self):
        return self.author 

class Source(models.Model):
    article = models.ForeignKey(Article)
    source = models.CharField(max_length=200)

    def __unicode__(self):
        return self.source

class Keyword(models.Model):
    article = models.ForeignKey(Article)
    keyword = models.CharField(max_length=200)

    def __unicode__(self):
        return self.keyword
