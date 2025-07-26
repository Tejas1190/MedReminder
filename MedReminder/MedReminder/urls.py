"""
URL configuration for MedReminder project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from MedReminder.Meds import views as meds_views
from MedReminder.Meds.views import home_view
from MedReminder.Meds.views import register_push, confirm_intake

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include(('MedReminder.Chat.urls', 'chat'), namespace='chat')),
    path('meds/', include(('MedReminder.Meds.urls', 'meds'), namespace='meds')),
    path('accounts/', include(('MedReminder.Accounts.urls', 'accounts'), namespace='accounts')),
    path('login/', lambda request: redirect('/accounts/login/', permanent=True)),
    path('register/', lambda request: redirect('/accounts/register/', permanent=True)),
    path('logout/', lambda request: redirect('/accounts/logout/', permanent=True)),
    # The following are direct view paths, not included in a namespace
    path('appointments/', meds_views.appointments_list, name='appointments_list'),
    path('appointments/add/', meds_views.appointments_add, name='appointments_add'),
    path('appointments/<int:appt_id>/edit/', meds_views.appointments_edit, name='appointments_edit'),
    path('appointments/<int:appt_id>/delete/', meds_views.appointments_delete, name='appointments_delete'),
    path('mood/', meds_views.mood_list, name='mood_list'),
    path('mood/add/', meds_views.mood_add, name='mood_add'),
    path('mood/<int:entry_id>/edit/', meds_views.mood_edit, name='mood_edit'),
    # Add geofencing URLs
    path('geofencing/', include(('MedReminder.Geofencing.urls', 'geofencing'), namespace='geofencing')),
    path('calendar/', meds_views.calendar_view, name='calendar_view'),
    path('dashboard/', meds_views.caregiver_dashboard, name='caregiver_dashboard'),
    path('pdf/', meds_views.pdf_history, name='pdf_history'),
    path('pdf/download/', meds_views.pdf_download, name='pdf_download'),
    path('intake_logs/', meds_views.intake_logs_list, name='intake_logs_list'),
    path('intake_logs/<int:log_id>/confirm/', meds_views.intake_log_confirm, name='intake_log_confirm'),
    path('', home_view, name='home'),
    # Add web push notification endpoints
    path('register-push/', register_push, name='register_push'),
    path('confirm-intake/', confirm_intake, name='confirm_intake'),
    path('test-push/', meds_views.test_web_push, name='test_web_push'),
]
