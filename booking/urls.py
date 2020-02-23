from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('admin/', views.admin_view, name='admin_view'),
    path('location/view/<int:id_loc>', views.location_view, name="location_view"),
    path('location/edit/', views.location_edit, name="location_edit"),
    path('location/view/add', views.location_add_view, name="location_add_view"),
    path('location/add/', views.location_add, name="location_add"),
    path('auth/', views.auth, name='auth'),
    path('', views.index, name='index'),
]