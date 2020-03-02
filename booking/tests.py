from django.test import RequestFactory, TestCase, Client
from booking import models
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ValidationError
from django.urls import reverse
from . import views
from datetime import datetime
import pytz
import json


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

        models.Reservation.objects.create(
            title="reunion",
            start_date=self.utc.localize(datetime(2019, 6, 1, 12, 00, 00)),
            end_date=self.utc.localize(datetime(2019, 6, 1, 13, 00, 00)),
            resource=self.rs1,
            owner=self.user1,
        )

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

    def test_rt_view_admin(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.get(reverse("rt_view", args=[1,]))
        self.assertEqual(response.status_code, 200)

    def test_rt_view_admin_not_exist(self):
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

    def test_rt_edit_user_get(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("rt_edit"))
        self.assertEqual(response.status_code, 405)

    def test_rt_edit_user_post(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.post(reverse("rt_edit"))
        self.assertRedirects(
            response,
            reverse("login_view") + "?next=/booking/rt/edit/",
            status_code=302,
            target_status_code=302,
        )

    def test_rt_edit_admin_post(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(reverse("rt_edit"))
        self.assertEqual(response.status_code, 400)

    def test_rt_edit_admin_post_ok(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(reverse("rt_edit"), {"id": 1, "name": "pad"})
        self.assertRedirects(
            response, reverse("admin_view"), status_code=302, target_status_code=200,
        )

    def test_rt_edit_admin_post_not_exist(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(reverse("rt_edit"), {"id": 2, "name": "pad"})
        self.assertEqual(response.status_code, 404)

    def test_resource_edit_user_get(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("resource_edit"))
        self.assertEqual(response.status_code, 405)

    def test_resource_edit_user_post(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.post(reverse("resource_edit"))
        self.assertRedirects(
            response,
            reverse("login_view") + "?next=/booking/resource/edit/",
            status_code=302,
            target_status_code=302,
        )

    def test_resource_edit_admin_post(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(reverse("resource_edit"))
        self.assertEqual(response.status_code, 400)

    def test_resource_edit_admin_post_ok(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(
            reverse("resource_edit"),
            {"id": 1, "word": "pad 32", "location": 1, "rt": 1},
        )
        self.assertRedirects(
            response, reverse("admin_view"), status_code=302, target_status_code=200,
        )

    def test_resource_edit_admin_post_not_exist(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(
            reverse("resource_edit"),
            {"id": 2, "word": "pad 32", "location": 1, "rt": 1},
        )
        self.assertEqual(response.status_code, 404)

    def test_location_add_user_get(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("location_add"))
        self.assertEqual(response.status_code, 405)

    def test_location_add_user_post(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.post(reverse("location_add"))
        self.assertRedirects(
            response,
            reverse("login_view") + "?next=/booking/location/add/",
            status_code=302,
            target_status_code=302,
        )

    def test_location_add_admin_post(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(reverse("location_add"))
        self.assertEqual(response.status_code, 400)

    def test_location_add_admin_post_ok(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(reverse("location_add"), {"name": "cuisine", "capacity": 2},)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.json())[0]
        self.assertEqual(data["fields"]["name"], "cuisine")
        self.assertEqual(data["fields"]["capacity"], "2")

    def test_rt_add_user_get(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("rt_add"))
        self.assertEqual(response.status_code, 405)

    def test_rt_add_user_post(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.post(reverse("rt_add"))
        self.assertRedirects(
            response,
            reverse("login_view") + "?next=/booking/rt/add/",
            status_code=302,
            target_status_code=302,
        )

    def test_rt_add_admin_post(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(reverse("rt_add"))
        self.assertEqual(response.status_code, 400)

    def test_rt_add_admin_post_ok(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(reverse("rt_add"), {"name": "test"},)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.json())[0]
        self.assertEqual(data["fields"]["name"], "test")

    def test_resource_add_user_get(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("resource_add"))
        self.assertEqual(response.status_code, 405)

    def test_resource_add_user_post(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.post(reverse("resource_add"))
        self.assertRedirects(
            response,
            reverse("login_view") + "?next=/booking/resource/add/",
            status_code=302,
            target_status_code=302,
        )

    def test_resource_add_admin_post(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(reverse("resource_add"))
        self.assertEqual(response.status_code, 400)

    def test_resource_add_admin_post_ok(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(
            reverse("resource_add"), {"word": "resource1", "location": 1, "rt": 1},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.json())[0]
        self.assertEqual(data["fields"]["word"], "resource1")
        self.assertEqual(data["fields"]["resource_type"], "écran")
        self.assertEqual(data["fields"]["location"][0], "salle de réunion 300")

    def test_resource_add_admin_post_ko(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(
            reverse("resource_add"), {"word": "resource1", "location": 2, "rt": 1},
        )
        self.assertEqual(response.status_code, 404)

    def test_reservation_add_user_get(self):
        c = Client()
        c.login(username="user", password="user")
        response = c.get(reverse("reservation_add"))
        self.assertEqual(response.status_code, 405)

    def test_reservation_add_admin_post(self):
        c = Client()
        c.login(username="admin", password="admin")
        response = c.post(reverse("reservation_add"))
        self.assertEqual(response.status_code, 400)

    def test_reservation_add_admin_post_ok(self):
        c = Client()
        c.login(username="admin", password="admin")
        input_formats = [
            "%Y-%m-%dT%H:%M",
        ]
        start_date = datetime(2020, 6, 1, 12, 00, 00).strftime("%Y-%m-%dT%H:%M")
        end_date = datetime(2020, 6, 1, 13, 00, 00).strftime("%Y-%m-%dT%H:%M")
        response = c.post(
            reverse("reservation_add"),
            {
                "id_resource": 1,
                "title": "V2",
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.json())[0]
        self.assertEqual(data["pk"], 2)
        self.assertEqual(data["fields"]["title"], "V2")
        self.assertEqual(data["fields"]["start_date"], "2020-06-01T12:00:00Z")
        self.assertEqual(data["fields"]["end_date"], "2020-06-01T13:00:00Z")
        self.assertEqual(data["fields"]["resource"][0], "capteur de présence ref 5478")
        self.assertEqual(data["fields"]["resource"][1], "salle de réunion 300")
        self.assertEqual(data["fields"]["owner"][0], "admin")

    def test_resource_add_admin_post_ko(self):
        c = Client()
        c.login(username="admin", password="admin")
        start_date = datetime(2025, 6, 1, 12, 00, 00).strftime("%Y-%m-%dT%H:%M")
        end_date = datetime(2025, 6, 1, 13, 00, 00).strftime("%Y-%m-%dT%H:%M")
        response = c.post(
            reverse("reservation_add"),
            {
                "id_resource": 2,
                "title": "V2",
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_reservation_add_admin_post_dates_reversed(self):
        c = Client()
        c.login(username="admin", password="admin")
        input_formats = [
            "%Y-%m-%dT%H:%M",
        ]
        start_date = datetime(2023, 6, 1, 12, 00, 00).strftime("%Y-%m-%dT%H:%M")
        end_date = datetime(2022, 6, 1, 13, 00, 00).strftime("%Y-%m-%dT%H:%M")
        response = c.post(
            reverse("reservation_add"),
            {
                "id_resource": 1,
                "title": "V2",
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b"start date must be before end date")

    def test_reservation_add_admin_post_dates_busy(self):
        c = Client()
        c.login(username="admin", password="admin")
        input_formats = [
            "%Y-%m-%dT%H:%M",
        ]
        start_date = datetime(2019, 6, 1, 12, 00, 00).strftime("%Y-%m-%dT%H:%M")
        end_date = datetime(2019, 6, 1, 13, 00, 00).strftime("%Y-%m-%dT%H:%M")
        response = c.post(
            reverse("reservation_add"),
            {
                "id_resource": 1,
                "title": "V2",
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b"already busy")
