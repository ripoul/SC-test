from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import AuthValidationForm

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
        return redirect(reverse('index'))
    else:
        return HttpResponse("can't login with provided credentials", status=403)

@login_required(login_url="/booking/login")
def logout_view(request):
    logout(request)
    return redirect(reverse('login_view'))