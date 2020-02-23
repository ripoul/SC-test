from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator

from booking.forms import AuthValidationForm, LocationValidationForm
from booking.models import Location, Reservation, Resource, ResourceType

@login_required(login_url="/booking/login")
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('index'))
    return render(request, 'booking/login.html')

@require_POST
def auth(request):
    form = AuthValidationForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(status=400)
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(username=email, password=password)
    if user is not None:
        login(request, user)
        if user.is_superuser:
            return redirect(reverse('admin_view'))
        return redirect(reverse('index'))
    else:
        return HttpResponse("can't login with provided credentials", status=403)

@login_required(login_url="/booking/login")
def logout_view(request):
    logout(request)
    return redirect(reverse('login_view'))

@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def admin_view(request):
    resources = Resource.objects.all()
    resourceTypes = ResourceType.objects.all()
    locations = Location.objects.all()
    context = {
        "resources":resources,
        "resourceTypes":resourceTypes,
        "locations":locations
    }
    return render(request, 'booking/admin.html', context)

@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def location_view(request, id_loc):
    location = Location.objects.get(id=id_loc)
    context = {
        "location":location
    }
    return render(request, 'booking/location.html', context)

@require_POST
@user_passes_test(lambda u: u.is_superuser)
@login_required(login_url="/booking/login")
def location_edit(request):
    form = LocationValidationForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse(status=400)
    id_loc = request.POST['id']
    name = request.POST['name']
    capacity = request.POST['capacity']

    location = Location.objects.get(id=id_loc)
    location.name = name
    location.capacity = capacity
    location.save()
    return redirect(reverse('admin_view'))