from django.urls import path
from .views import (
    meds_list, meds_add, meds_edit, meds_delete,
    schedules_list, schedules_add, schedules_edit, schedules_delete,
    intake_logs_list, intake_log_confirm,
    appointments_list, appointments_add, appointments_edit, appointments_delete,
    mood_list, mood_add, mood_edit, mood_delete,
    calendar_view,
    caregiver_dashboard,
    pdf_history, pdf_download
)

urlpatterns = [
    path('', meds_list, name='meds_list'),
    path('add/', meds_add, name='meds_add'),
    path('<int:med_id>/edit/', meds_edit, name='meds_edit'),
    path('<int:med_id>/delete/', meds_delete, name='meds_delete'),
    path('<int:med_id>/schedules/', schedules_list, name='schedules_list'),
    path('<int:med_id>/schedules/add/', schedules_add, name='schedules_add'),
    path('<int:med_id>/schedules/<int:schedule_id>/edit/', schedules_edit, name='schedules_edit'),
    path('<int:med_id>/schedules/<int:schedule_id>/delete/', schedules_delete, name='schedules_delete'),
    path('intake_logs/', intake_logs_list, name='intake_logs_list'),
    path('intake_logs/<int:log_id>/confirm/', intake_log_confirm, name='intake_log_confirm'),
    path('appointments/', appointments_list, name='appointments_list'),
    path('appointments/add/', appointments_add, name='appointments_add'),
    path('appointments/<int:appt_id>/edit/', appointments_edit, name='appointments_edit'),
    path('appointments/<int:appt_id>/delete/', appointments_delete, name='appointments_delete'),
    path('mood/', mood_list, name='mood_list'),
    path('mood/add/', mood_add, name='mood_add'),
    path('mood/<int:entry_id>/edit/', mood_edit, name='mood_edit'),
    path('mood/<int:entry_id>/delete/', mood_delete, name='mood_delete'),
    path('mood/<int:entry_id>/delete/', mood_delete, name='mood_delete'),
    path('calendar/', calendar_view, name='calendar_view'),
    path('dashboard/', caregiver_dashboard, name='caregiver_dashboard'),
    path('pdf/', pdf_history, name='pdf_history'),
    path('pdf/download/', pdf_download, name='pdf_download'),
] 