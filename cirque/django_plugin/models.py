from django.db import models


class CJDNSRoute(models.Model):
    ip = models.GenericIPAddressField()
    link = models.IntegerField()
    version = models.IntegerField()
    path = models.CharField(max_length=100)
