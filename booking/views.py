from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.core import serializers
from django.core.exceptions import ValidationError

from booking.forms import (
    AuthValidationForm,
    LocationValidationForm,
    LocationAddValidationForm,
    RtValidationForm,
    RtAddValidationForm,
    ResourceValidationForm,
    ResourceAddValidationForm,
    ReservationDeleteValidationForm,
    ReservationAddValidationForm,
)
from booking.models import Location, Reservation, Resource, ResourceType

from datetime import datetime
import pytz


def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse("index"))
    return render(request, "booking/login.html")


@require_POST
def auth(request):
    form = AuthValidationForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(status=400)
    email = request.POST["email"]
    password = request.POST["password"]
    user = authenticate(username=email, password=password)
    if user is not None:
        login(request, user)
        if user.is_superuser:
            return redirect(reverse("admin_view"))
        return redirect(reverse("index"))
    else:
        return HttpResponse("can't login with provided credentials", status=403)


@login_required(login_url="/booking/login")
def logout_view(request):
    logout(request)
    return redirect(reverse("login_view"))


@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def admin_view(request):
    resources = Resource.objects.all()
    resourceTypes = ResourceType.objects.all()
    locations = Location.objects.all()
    context = {
        "resources": resources,
        "resourceTypes": resourceTypes,
        "locations": locations,
    }
    return render(request, "booking/admin.html", context)


@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def location_view(request, id_loc):
    location = Location.objects.get(id=id_loc)
    context = {"location": location}
    return render(request, "booking/location_edit.html", context)


@require_POST
@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def location_edit(request):
    form = LocationValidationForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(status=400)
    id_loc = request.POST["id"]
    name = request.POST["name"]
    capacity = request.POST["capacity"]

    location = Location.objects.get(id=id_loc)
    location.name = name
    location.capacity = capacity
    location.save()
    return redirect(reverse("admin_view"))


@require_POST
@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def location_add(request):
    form = LocationAddValidationForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(status=400)
    name = request.POST["name"]
    capacity = request.POST["capacity"]
    loc = Location.objects.create(name=name, capacity=capacity)
    return JsonResponse(serializers.serialize("json", [loc,]), safe=False)


@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def rt_view(request, id_rt):
    rt = ResourceType.objects.get(id=id_rt)
    context = {"ResourceType": rt}
    return render(request, "booking/rt_edit.html", context)


@require_POST
@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def rt_edit(request):
    form = RtValidationForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(status=400)
    id_rt = request.POST["id"]
    name = request.POST["name"]
    rt = ResourceType.objects.get(id=id_rt)
    rt.name = name
    rt.save()
    return redirect(reverse("admin_view"))


@require_POST
@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def rt_add(request):
    form = RtAddValidationForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(status=400)
    name = request.POST["name"]
    rt = ResourceType.objects.create(name=name)
    return JsonResponse(serializers.serialize("json", [rt,]), safe=False)


@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def resource_view(request, id_resource):
    resource = Resource.objects.get(id=id_resource)
    resourceTypes = ResourceType.objects.all()
    locations = Location.objects.all()
    context = {
        "resource": resource,
        "resourceTypes": resourceTypes,
        "locations": locations,
    }
    return render(request, "booking/resource_edit.html", context)


@require_POST
@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def resource_edit(request):
    form = ResourceValidationForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(status=400)
    id_resource = request.POST["id"]
    word = request.POST["word"]
    location_id = request.POST["location"]
    rt_id = request.POST["location"]
    rt = ResourceType.objects.get(id=rt_id)
    location = Location.objects.get(id=location_id)

    resource = Resource.objects.get(id=id_resource)
    resource.word = word
    resource.location = location
    resource.ResourceType = rt
    resource.save()
    return redirect(reverse("admin_view"))


@require_POST
@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def resource_add(request):
    form = ResourceAddValidationForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(status=400)
    word = request.POST["word"]
    location_id = request.POST["location"]
    rt_id = request.POST["rt"]
    rt = ResourceType.objects.get(id=rt_id)
    location = Location.objects.get(id=location_id)

    resource = Resource.objects.create(word=word, resource_type=rt, location=location)
    return JsonResponse(
        serializers.serialize("json", [resource,], use_natural_foreign_keys=True),
        safe=False,
    )


@login_required(login_url="/booking/login")
def index(request):
    resources = Resource.objects.all()
    if request.user.is_superuser:
        reservations_user = Reservation.objects.all()
    else:
        reservations_user = Reservation.objects.filter(owner=request.user)

    context = {
        "form_add_reservation": ReservationAddValidationForm,
        "resources": resources,
        "reservations_user": reservations_user,
    }
    return render(request, "booking/index.html", context)


@require_POST
@login_required(login_url="/booking/login")
def delete_reservation(request):
    form = ReservationDeleteValidationForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(status=400)
    id_reservation = request.POST["id"]

    reservation = Reservation.objects.get(id=id_reservation)

    if reservation.owner != request.user and not request.user.is_superuser:
        return HttpResponse(status=403)
    reservation.delete()
    return HttpResponse(status=204)


@require_POST
@login_required(login_url="/booking/login")
def reservation_add(request):
    form = ReservationAddValidationForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(status=400)
    id_resource = request.POST["id_resource"]
    title = request.POST["title"]
    start_date = request.POST["start_date"]  #
    end_date = request.POST["end_date"]  #%Y-%m-%dT%H:%M

    resource = Resource.objects.get(id=id_resource)
    utc = pytz.UTC
    start_date = utc.localize(datetime.strptime(start_date, "%Y-%m-%dT%H:%M"))
    end_date = utc.localize(datetime.strptime(end_date, "%Y-%m-%dT%H:%M"))

    try:
        reservation = Reservation.create(
            title=title,
            start_date=start_date,
            end_date=end_date,
            resource=resource,
            owner=request.user,
        )
        reservation.save()
    except ValidationError as e:
        return HttpResponse(e.message, status=400)

    return JsonResponse(
        serializers.serialize("json", [reservation,], use_natural_foreign_keys=True),
        safe=False,
    )
