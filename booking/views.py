from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.cache import cache

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
import asyncio
import websockets


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
    if cache.has_key("resources"):
        resources = cache.get("resources")
    else:
        resources = Resource.objects.all()
        cache.set("resources", resources)

    if cache.has_key("rt"):
        resourceTypes = ResourceType.objects.all()
    else:
        resourceTypes = ResourceType.objects.all()
        cache.set("rt", resourceTypes)

    if cache.has_key("locations"):
        locations = Location.objects.all()
    else:
        locations = Location.objects.all()
        cache.set("locations", locations)

    context = {
        "resources": resources,
        "resourceTypes": resourceTypes,
        "locations": locations,
    }
    return render(request, "booking/admin.html", context)


@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def location_view(request, id_loc):
    try:
        location = Location.objects.get(id=id_loc)
    except Location.DoesNotExist:
        raise (Http404("Location does not exist"))

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

    try:
        location = Location.objects.get(id=id_loc)
    except Location.DoesNotExist:
        raise (Http404("Location does not exist"))
    location.name = name
    location.capacity = capacity
    location.save()
    cache.delete("locations")
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
    cache.delete("locations")
    return JsonResponse(serializers.serialize("json", [loc,]), safe=False)


@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def rt_view(request, id_rt):
    try:
        rt = ResourceType.objects.get(id=id_rt)
    except ResourceType.DoesNotExist:
        raise (Http404("Resource type does not exist"))
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
    try:
        rt = ResourceType.objects.get(id=id_rt)
    except ResourceType.DoesNotExist:
        raise (Http404("Resource Type does not exist"))
    rt.name = name
    rt.save()
    cache.delete("rt")
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
    cache.delete("rt")
    return JsonResponse(serializers.serialize("json", [rt,]), safe=False)


@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def resource_view(request, id_resource):
    try:
        resource = Resource.objects.get(id=id_resource)
    except Resource.DoesNotExist:
        raise (Http404("Resource does not exist"))
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
    rt_id = request.POST["rt"]

    try:
        resource = Resource.objects.get(id=id_resource)
    except Resource.DoesNotExist:
        raise (Http404("Resource does not exist"))

    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        raise (Http404("Location does not exist"))

    try:
        rt = ResourceType.objects.get(id=rt_id)
    except ResourceType.DoesNotExist:
        raise (Http404("Resource Type does not exist"))

    resource.word = word
    resource.location = location
    resource.ResourceType = rt
    resource.save()
    cache.delete("resources")
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

    try:
        rt = ResourceType.objects.get(id=rt_id)
    except ResourceType.DoesNotExist:
        raise (Http404("Resource Type does not exist"))

    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        raise (Http404("Location does not exist"))

    resource = Resource.objects.create(word=word, resource_type=rt, location=location)
    cache.delete("resources")
    return JsonResponse(
        serializers.serialize("json", [resource,], use_natural_foreign_keys=True),
        safe=False,
    )


@login_required(login_url="/booking/login")
def index(request):
    if cache.has_key("resources"):
        resources = cache.get("resources")
    else:
        resources = Resource.objects.all()
        cache.set("resources", resources)
    if cache.has_key("reservations"):
        reservations = cache.get("reservations")
    else:
        reservations = Reservation.objects.all()
        cache.set("reservations", reservations)

    context = {
        "resources": resources,
        "reservations_user": reservations,
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
    cache.delete("reservations")

    if reservation.owner != request.user and not request.user.is_superuser:
        return HttpResponse(status=403)
    reservation.delete()
    return HttpResponse(status=204)


async def send_msg(msg, socketURL):
    async with websockets.connect(socketURL) as websocket:
        try:
            await websocket.send(msg)
        except Exception as e:
            print(e)


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

    try:
        resource = Resource.objects.get(id=id_resource)
    except Resource.DoesNotExist:
        raise (Http404("Resource does not exist"))

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
    cache.delete("reservations")

    msg = serializers.serialize("json", [reservation,], use_natural_foreign_keys=True)

    if "https" in request.META["wsgi.url_scheme"]:
        socketURL = "wss://"
    else:
        socketURL = "ws://"
    socketURL = f"{socketURL}{request.META['HTTP_HOST']}/ws"

    loop = asyncio.get_event_loop()
    task_obj = loop.create_task(send_msg(msg, socketURL))

    return JsonResponse(msg, safe=False,)
