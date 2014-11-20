from django.db import models

# Create your models here.

class Article(models.Model):
    url = models.URLField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    date_added = models.DateTimeField('Date Added', blank=True, null=True)
    date_published = models.DateTimeField('Date Published', blank=True, null=True)
    influence = models.IntegerField(default=0)

    def __unicode__(self):
        if len(self.title) >= 30:
            return self.title[:27] + '...'
        return self.title

    def natural_key(self):
        return self.url


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
