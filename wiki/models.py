from django.db import models
from datetime import datetime

# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=16)
    email = models.CharField(max_length=100)

class Article(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=32)
    content = models.TextField()
    content_html = models.TextField()
    time_create = models.DateTimeField(default=datetime.now, auto_now_add = True)
    time_edit = models.DateTimeField(default=datetime.now, auto_now_add = True)
    links = models.TextField(default='')

class Media(models.Model):
    filename = models.CharField(max_length=256)
    time_create = models.DateTimeField(default=datetime.now, auto_now_add = True)

class History(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=32)

    author = models.ManyToManyField(Author)
    content = models.TextField(default='')
    time = models.DateTimeField(auto_now_add = True)
    type = models.CharField(max_length=16, default='mod')

class Settings(models.Model):
    mainpage = models.ForeignKey(Article)
    path = models.CharField(max_length=999)
