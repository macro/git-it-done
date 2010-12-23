from django.db import models


class Task(models.Model):
    name = models.CharField(max_length=512)
    description = models.TextField(blank=True)
    hash = models.CharField(max_length=40)

    completed = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

