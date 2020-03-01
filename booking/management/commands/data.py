from datetime import datetime
import booking.models as models
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create some data for testing"

    def handle(self, *args, **options):
        rt1 = models.ResourceType.objects.create(name="écran")
        rt2 = models.ResourceType.objects.create(name="capteur")
        rt3 = models.ResourceType.objects.create(name="pad")

        loc1 = models.Location.objects.create(name="salle de réunion 300", capacity=32)

        rs1 = models.Resource.objects.create(
            resource_type=rt2, word="capteur de présence ref 5478", location=loc1
        )

        rs2 = models.Resource.objects.create(
            resource_type=rt3, word="pad ref 1058", location=loc1
        )

        user1 = User.objects.create_user("user", "user@example.com", "user")
        admin1 = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin"
        )

        models.Reservation.objects.create(
            title="reunion",
            start_date=datetime(2019, 6, 1, 12, 00, 00),
            end_date=datetime(2019, 6, 1, 13, 00, 00),
            resource=rs1,
            owner=user1,
        )
        models.Reservation.objects.create(
            title="reunion2",
            start_date=datetime(2019, 6, 1, 13, 00, 00),
            end_date=datetime(2019, 6, 1, 14, 00, 00),
            resource=rs1,
            owner=user1,
        )

        models.Reservation.objects.create(
            title="reunion",
            start_date=datetime(2020, 6, 1, 12, 00, 00),
            end_date=datetime(2020, 6, 1, 13, 00, 00),
            resource=rs1,
            owner=user1,
        )
        models.Reservation.objects.create(
            title="reunion2",
            start_date=datetime(2020, 6, 1, 13, 00, 00),
            end_date=datetime(2020, 6, 1, 14, 00, 00),
            resource=rs1,
            owner=user1,
        )

        self.stdout.write(self.style.SUCCESS("all data created"))
