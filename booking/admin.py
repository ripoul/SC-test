from django.contrib import admin
from booking.models import Reservation, Resource, ResourceType, Location

# Register your models here.
admin.site.register(Reservation)
admin.site.register(Resource)
admin.site.register(ResourceType)
admin.site.register(Location)
