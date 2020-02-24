from django.db import models
from django.contrib.auth.models import User


class ResourceType(models.Model):
    name = models.CharField(max_length=200)

    def natural_key(self):
        return (self.name)


class Location(models.Model):
    name = models.CharField(max_length=200)
    capacity = models.IntegerField()
    
    def natural_key(self):
        return (self.name,)


class Resource(models.Model):
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    word = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)


class Reservation(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField(auto_now=False)
    end_date = models.DateTimeField(auto_now=False)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
