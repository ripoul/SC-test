from django.test import RequestFactory, TestCase, Client
from booking import models
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ValidationError
from django.urls import reverse
from . import views
from datetime import datetime
import pytz


class dataForTests(TestCase):
    def setUp(self):
        self.rt1 = models.ResourceType.objects.create(name="écran")

        self.loc1 = models.Location.objects.create(
            name="salle de réunion 300", capacity=32
        )

        self.rs1 = models.Resource.objects.create(
            resource_type=self.rt1,
            word="capteur de présence ref 5478",
            location=self.loc1,
        )

        self.user1 = User.objects.create_user("user", "user@example.com", "user")
        self.admin1 = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin"
        )

        self.utc = pytz.UTC

        models.Reservation.create(
            title="reunion",
            start_date=self.utc.localize(datetime(2019, 6, 1, 12, 00, 00)),
            end_date=self.utc.localize(datetime(2019, 6, 1, 13, 00, 00)),
            resource=self.rs1,
            owner=self.user1,
        ).save()

        self.factory = RequestFactory()


class ReservationModelTests(dataForTests):
    def test_same_time_reservation(self):
        with self.assertRaisesMessage(ValidationError, "already busy"):
            models.Reservation.create(
                title="reunion",
                start_date=self.utc.localize(datetime(2019, 6, 1, 12, 00, 00)),
                end_date=self.utc.localize(datetime(2019, 6, 1, 13, 00, 00)),
                resource=self.rs1,
                owner=self.user1,
            )

    def test_start_date_after_end_date(self):
        with self.assertRaisesMessage(
            ValidationError, "start date must be before end date"
        ):
            models.Reservation.create(
                title="reunion",
                start_date=self.utc.localize(datetime(2021, 6, 1, 12, 00, 00)),
                end_date=self.utc.localize(datetime(2020, 6, 1, 13, 00, 00)),
                resource=self.rs1,
                owner=self.user1,
            )


class bookingTests(dataForTests):
    def test_logout_no_connected(self):
        c = Client()
        response = c.get(reverse("logout_view"))
        self.assertRedirects(
            response,
            reverse("login_view")[:-1] + "?next=/booking/logout/",
            status_code=302,
            target_status_code=301,
        )

    def test_logout_connected(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("logout_view"))
        self.assertRedirects(
            response, reverse("login_view"), status_code=302, target_status_code=200
        )

    def test_login_connected(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("login_view"))
        self.assertRedirects(
            response, reverse("index"), status_code=302, target_status_code=200
        )

    def test_admin_connected_user(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("admin_view"))
        self.assertRedirects(
            response,
            reverse("login_view") + "?next=%2Fbooking%2Fadmin%2F",
            status_code=302,
            target_status_code=302,
        )

    def test_admin_connected(self):
        request = self.factory.get(reverse("admin_view"))
        request.user = self.admin1
        response = views.admin_view(request)
        self.assertEqual(response.status_code, 200)

    def test_logout_connected(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("logout_view"))
        self.assertRedirects(
            response, reverse("login_view"), status_code=302, target_status_code=200
        )

    def test_location_view_user(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("location_view", args=[1,]))
        self.assertRedirects(
            response,
            reverse("login_view") + "?next=/booking/location/view/1",
            status_code=302,
            target_status_code=302,
        )

    def test_location_view_admin(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.get(reverse("location_view", args=[1,]))
        self.assertEqual(response.status_code, 200)

    def test_location_view_admin_not_exist(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.get(reverse("location_view", args=[2,]))
        self.assertEqual(response.status_code, 404)

    def test_rt_view_user(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("rt_view", args=[1,]))
        self.assertRedirects(
            response,
            reverse("login_view") + "?next=/booking/rt/view/1",
            status_code=302,
            target_status_code=302,
        )

    def test_location_view_admin(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.get(reverse("rt_view", args=[1,]))
        self.assertEqual(response.status_code, 200)

    def test_location_view_admin_not_exist(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.get(reverse("rt_view", args=[2,]))
        self.assertEqual(response.status_code, 404)

    def test_resource_view_user(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("resource_view", args=[1,]))
        self.assertRedirects(
            response,
            reverse("login_view") + "?next=/booking/resource/view/1",
            status_code=302,
            target_status_code=302,
        )

    def test_resource_view_admin(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.get(reverse("resource_view", args=[1,]))
        self.assertEqual(response.status_code, 200)

    def test_resource_view_admin_not_exist(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.get(reverse("resource_view", args=[2,]))
        self.assertEqual(response.status_code, 404)

    def test_location_edit_user_get(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("location_edit"))
        self.assertEqual(response.status_code, 405)

    def test_location_edit_user_post(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.post(reverse("location_edit"))
        self.assertRedirects(
            response,
            reverse("login_view") + "?next=/booking/location/edit/",
            status_code=302,
            target_status_code=302,
        )

    def test_location_edit_admin_post(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(reverse("location_edit"))
        self.assertEqual(response.status_code, 400)

    def test_location_edit_admin_post_ok(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(
            reverse("location_edit"), {"id": 1, "name": "cuisine", "capacity": 32}
        )
        self.assertRedirects(
            response, reverse("admin_view"), status_code=302, target_status_code=200,
        )

    def test_location_edit_admin_post_not_exist(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(
            reverse("location_edit"), {"id": 2, "name": "cuisine", "capacity": 32}
        )
        self.assertEqual(response.status_code, 404)
