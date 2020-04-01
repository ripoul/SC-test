from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

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

    @classmethod
    def create(cls, title, start_date, end_date, resource, owner):        
        overlapping = resource.reservations.filter(
            Q(start_date__gte=start_date, start_date__lte=end_date) | Q(end_date__gte=start_date, end_date__lte=end_date)
        ).count()

        if overlapping > 0:
            raise ValidationError(_("already busy"))

        if start_date >= end_date:
            raise ValidationError(_("start date must be before end date"))
        reservation = cls(
            title=title,
            start_date=start_date,
            end_date=end_date,
            resource=resource,
            owner=owner,
        )

        if reservation.is_past:
            raise ValidationError(_("the reservation have to be not passed"))

        return reservation

    @property
    def is_past(self):
        utc = pytz.UTC
        return utc.localize(datetime.now()) > self.start_date
