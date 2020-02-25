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

    def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:    #edge case
            overlap = False
        elif (new_start >= fixed_start and new_start <= fixed_end) or (new_end >= fixed_start and new_end <= fixed_end): #innner limits
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end: #outter limits
            overlap = True
 
        return overlap
