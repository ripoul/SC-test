from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("admin/", views.admin_view, name="admin_view"),
    path("location/view/<int:id_loc>", views.location_view, name="location_view"),
    path("location/edit/", views.location_edit, name="location_edit"),
    path("location/add/", views.location_add, name="location_add"),
    path("rt/view/<int:id_rt>", views.rt_view, name="rt_view"),
    path("rt/edit/", views.rt_edit, name="rt_edit"),
    path("rt/add/", views.rt_add, name="rt_add"),
    path("resource/view/<int:id_resource>", views.resource_view, name="resource_view"),
    path("resource/edit/", views.resource_edit, name="resource_edit"),
    path("resource/add/", views.resource_add, name="resource_add"),
    path("reservation/delete/", views.delete_reservation, name="reservation_delete"),
    path("reservation/add/", views.reservation_add, name="reservation_add"),
    path("auth/", views.auth, name="auth"),
    path("", views.index, name="index"),
]
