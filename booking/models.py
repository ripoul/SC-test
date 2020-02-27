from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from datetime import datetime
import pytz

class ResourceType(models.Model):
    name = models.CharField(max_length=200)

    def natural_key(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=200)
    capacity = models.IntegerField()

    def natural_key(self):
        return (self.name,)


class Resource(models.Model):
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    word = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def natural_key(self):
        return (self.word, self.location.name)


class Reservation(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField(auto_now=False)
    end_date = models.DateTimeField(auto_now=False)
    resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, related_name="reservations"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def check_overlap(self, new_start, new_end):
        overlap = False
        if new_start == self.end_date or new_end == self.start_date:  # edge case
            overlap = False
        elif (new_start >= self.start_date and new_start <= self.end_date) or (
            new_end >= self.start_date and new_end <= self.end_date
        ):  # innner limits
            overlap = True
        elif new_start <= self.start_date and new_end >= self.end_date:  # outter limits
            overlap = True

        return overlap

    @classmethod
    def create(cls, title, start_date, end_date, resource, owner):
        for reservation in resource.reservations.all():
            if reservation.check_overlap(start_date, end_date):
                raise ValidationError("already busy")
        
        if start_date>=end_date:
            raise ValidationError("start date must be before end date")
        reservation = cls(title=title, start_date=start_date, end_date=end_date, resource=resource, owner=owner)
        return reservation
    
    @property
    def is_past(self):
        utc = pytz.UTC
        return utc.localize(datetime.now()) > self.start_date