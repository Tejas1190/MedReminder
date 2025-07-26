from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Medication, MedicationSchedule, MedicationIntakeLog, Appointment, MoodTracker
from django import forms
from django.utils import timezone
import calendar
from datetime import date, timedelta, datetime
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

# Web Push Notification Endpoints
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import WebPushSubscription
import json

@csrf_exempt
@login_required
def register_push(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sub, created = WebPushSubscription.objects.get_or_create(
            user=request.user,
            endpoint=data['endpoint'],
            defaults={'p256dh': data['keys']['p256dh'], 'auth': data['keys']['auth']}
        )
        if not created:
            sub.p256dh = data['keys']['p256dh']
            sub.auth = data['keys']['auth']
            sub.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required
def confirm_intake(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        log_id = data.get('log_id')
        try:
            log = MedicationIntakeLog.objects.get(id=log_id, user=request.user)
            log.taken = True
            log.confirmed_at = timezone.now()
            log.save()
            return JsonResponse({'status': 'confirmed'})
        except MedicationIntakeLog.DoesNotExist:
            return JsonResponse({'status': 'not found'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def mood_delete(request, entry_id):
    entry = get_object_or_404(MoodTracker, id=entry_id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        return redirect('meds:mood_list')
    return render(request, 'mood_confirm_delete.html', {'mood': entry})

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'dosage', 'instructions', 'inventory_count']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[var(--primary-color)] focus:border-[var(--primary-color)] transition-shadow',
                'placeholder': 'e.g., Metformin'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[var(--primary-color)] focus:border-[var(--primary-color)] transition-shadow',
                'placeholder': 'e.g., 500mg, one tablet with breakfast',
                'rows': 3
            }),
            'inventory_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[var(--primary-color)] focus:border-[var(--primary-color)] transition-shadow',
                'placeholder': 'e.g., 90'
            })
        }

class MedicationScheduleForm(forms.ModelForm):
    class Meta:
        model = MedicationSchedule
        fields = ['time', 'days_of_week', 'caregiver']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor_name', 'date', 'time', 'notes']

class MoodTrackerForm(forms.ModelForm):
    class Meta:
        model = MoodTracker
        fields = ['date', 'mood', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'mood': forms.NumberInput(attrs={'min': 1, 'max': 10, 'type': 'number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.initial.get('date'):
            self.initial['date'] = timezone.now().date()

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Medication, MedicationSchedule, MedicationIntakeLog, Appointment, MoodTracker
from django import forms
from django.utils import timezone
import calendar
from datetime import date, timedelta, datetime
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

@login_required
def meds_list(request):
    medications = Medication.objects.filter(user=request.user)
    for med in medications:
        # Find the next scheduled intake log that is in the future
        next_log = med.intake_logs.filter(scheduled_time__gte=timezone.now(), taken=False).order_by('scheduled_time').first()
        if next_log:
            med.next_dose_time = timezone.localtime(next_log.scheduled_time).strftime('%I:%M %p')
            med.next_dose_note = timezone.localtime(next_log.scheduled_time).strftime('%A, %d %b %Y')
        else:
            # Fallback: compute from MedicationSchedule
            next_time = None
            next_day = None
            now = timezone.localtime(timezone.now())
            schedules = med.schedules.all()
            soonest_dt = None
            for sched in schedules:
                sched_days = [d.strip() for d in sched.days_of_week.split(',')] if sched.days_of_week != 'daily' else ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
                for i in range(8):  # look ahead up to a week
                    candidate_date = now.date() + timedelta(days=i)
                    weekday_str = candidate_date.strftime('%a')
                    if 'daily' in sched_days or weekday_str in sched_days:
                        candidate_dt = datetime.combine(candidate_date, sched.time)
                        candidate_dt = timezone.make_aware(candidate_dt)
                        if candidate_dt > now and (soonest_dt is None or candidate_dt < soonest_dt):
                            soonest_dt = candidate_dt
            if soonest_dt:
                med.next_dose_time = soonest_dt.strftime('%I:%M %p')
                med.next_dose_note = soonest_dt.strftime('%A, %d %b %Y')
            else:
                med.next_dose_time = None
                med.next_dose_note = ''
    return render(request, 'meds_list.html', {'medications': medications})

@login_required
def meds_add(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            med = form.save(commit=False)
            med.user = request.user
            med.save()
            return redirect('meds:meds_list')
    else:
        form = MedicationForm()
    return render(request, 'meds_form.html', {'form': form, 'form_title': 'Add Medication'})

@login_required
def meds_edit(request, med_id):
    med = get_object_or_404(Medication, id=med_id, user=request.user)
    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=med)
        if form.is_valid():
            form.save()
            return redirect('meds:meds_list')
    else:
        form = MedicationForm(instance=med)
    return render(request, 'meds_form.html', {'form': form, 'form_title': 'Edit Medication'})

@login_required
def meds_delete(request, med_id):
    med = get_object_or_404(Medication, id=med_id, user=request.user)
    if request.method == 'POST':
        med.delete()
        return redirect('meds:meds_list')
    return render(request, 'meds_confirm_delete.html', {'medication': med})

@login_required
def schedules_list(request, med_id):
    medication = get_object_or_404(Medication, id=med_id, user=request.user)
    schedules = MedicationSchedule.objects.filter(medication=medication)  # type: ignore
    return render(request, 'schedules_list.html', {'medication': medication, 'schedules': schedules})

@login_required
def schedules_add(request, med_id):
    medication = get_object_or_404(Medication, id=med_id, user=request.user)
    days_of_week_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    if request.method == 'POST':
        post_data = request.POST.copy()
        days_selected = post_data.getlist('days_of_week')
        if days_selected:
            post_data['days_of_week'] = ','.join(days_selected)
        form = MedicationScheduleForm(post_data)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.medication = medication
            schedule.save()

            # Schedule reminders for the next 7 days
            from .tasks import send_med_reminder
            import datetime
            now = timezone.localtime(timezone.now())
            days = [d.strip() for d in schedule.days_of_week.split(',')] if schedule.days_of_week != 'daily' else ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
            for i in range(7):
                candidate_date = now.date() + timedelta(days=i)
                weekday_str = candidate_date.strftime('%a')
                if 'daily' in days or weekday_str in days:
                    candidate_dt = datetime.datetime.combine(candidate_date, schedule.time)
                    candidate_dt = timezone.make_aware(candidate_dt)
                    if candidate_dt > now:
                        send_med_reminder.apply_async(args=[medication.id], eta=candidate_dt)
            return redirect('meds:schedules_list', med_id=medication.id)
    else:
        form = MedicationScheduleForm()
    return render(request, 'schedules_form.html', {'form': form, 'form_title': 'Add Schedule', 'medication': medication, 'days_of_week_list': days_of_week_list})

@login_required
def schedules_edit(request, med_id, schedule_id):
    medication = get_object_or_404(Medication, id=med_id, user=request.user)
    schedule = get_object_or_404(MedicationSchedule, id=schedule_id, medication=medication)
    days_of_week_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    if request.method == 'POST':
        post_data = request.POST.copy()
        days_selected = post_data.getlist('days_of_week')
        if days_selected:
            post_data['days_of_week'] = ','.join(days_selected)
        form = MedicationScheduleForm(post_data, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect('meds:schedules_list', med_id=medication.id)
    else:
        form = MedicationScheduleForm(instance=schedule)
    return render(request, 'schedules_form.html', {'form': form, 'form_title': 'Edit Schedule', 'medication': medication, 'days_of_week_list': days_of_week_list})

@login_required
def schedules_delete(request, med_id, schedule_id):
    medication = get_object_or_404(Medication, id=med_id, user=request.user)
    schedule = get_object_or_404(MedicationSchedule, id=schedule_id, medication=medication)
    if request.method == 'POST':
        schedule.delete()
        return redirect('meds:schedules_list', med_id=medication.id)
    return render(request, 'schedules_confirm_delete.html', {'medication': medication, 'schedule': schedule})

@login_required
def intake_logs_list(request):
    intake_logs = MedicationIntakeLog.objects.filter(user=request.user).order_by('-scheduled_time')  # type: ignore
    return render(request, 'intake_logs_list.html', {'intake_logs': intake_logs})

@login_required
def intake_log_confirm(request, log_id):
    log = get_object_or_404(MedicationIntakeLog, id=log_id, user=request.user)
    if request.method == 'POST' and not log.taken and not log.missed:
        log.taken = True
        log.confirmed_at = timezone.now()
        log.save()
    return redirect('intake_logs_list')

@login_required
def appointments_list(request):
    appointments = Appointment.objects.filter(user=request.user).order_by('-date', '-time')  # type: ignore
    return render(request, 'appointments_list.html', {'appointments': appointments})

@login_required
def appointments_add(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.user = request.user
            appt.save()
            return redirect('meds:appointments_list')
    else:
        form = AppointmentForm()
    return render(request, 'appointments_form.html', {'form': form, 'form_title': 'Add Appointment'})

@login_required
def appointments_edit(request, appt_id):
    appt = get_object_or_404(Appointment, id=appt_id, user=request.user)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appt)
        if form.is_valid():
            form.save()
            return redirect('appointments_list')
    else:
        form = AppointmentForm(instance=appt)
    return render(request, 'appointments_form.html', {'form': form, 'form_title': 'Edit Appointment'})

@login_required
def appointments_delete(request, appt_id):
    appt = get_object_or_404(Appointment, id=appt_id, user=request.user)
    if request.method == 'POST':
        appt.delete()
        return redirect('appointments_list')
    return render(request, 'appointments_confirm_delete.html', {'appointment': appt})

@login_required
def mood_list(request):
    moods = MoodTracker.objects.filter(user=request.user).order_by('-date')  # type: ignore
    return render(request, 'mood_list.html', {'moods': moods})

@login_required
def mood_add(request):
    if request.method == 'POST':
        form = MoodTrackerForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('meds:mood_list')
    else:
        form = MoodTrackerForm()
    return render(request, 'mood_form.html', {'form': form, 'form_title': 'Add Mood Entry'})

@login_required
def mood_edit(request, entry_id):
    entry = get_object_or_404(MoodTracker, id=entry_id, user=request.user)
    if request.method == 'POST':
        form = MoodTrackerForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('mood_list')
    else:
        form = MoodTrackerForm(instance=entry)
    return render(request, 'mood_form.html', {'form': form, 'form_title': 'Edit Mood Entry'})

@login_required
def calendar_view(request):
    today = date.today()
    year = today.year
    month = today.month
    cal = calendar.Calendar()
    # Gather all logs, moods, and appointments for the month
    month_logs = MedicationIntakeLog.objects.filter(user=request.user, scheduled_time__year=year, scheduled_time__month=month)  # type: ignore
    month_moods = MoodTracker.objects.filter(user=request.user, date__year=year, date__month=month)  # type: ignore
    month_appts = Appointment.objects.filter(user=request.user, date__year=year, date__month=month)  # type: ignore
    # Organize by day
    days = {}
    for log in month_logs:
        d = log.scheduled_time.day
        days.setdefault(d, {'intake_logs': [], 'mood_entries': [], 'appointments': []})
        days[d]['intake_logs'].append(log)
    for mood in month_moods:
        d = mood.date.day
        days.setdefault(d, {'intake_logs': [], 'mood_entries': [], 'appointments': []})
        days[d]['mood_entries'].append(mood)
    for appt in month_appts:
        d = appt.date.day
        days.setdefault(d, {'intake_logs': [], 'mood_entries': [], 'appointments': []})
        days[d]['appointments'].append(appt)
    # Build calendar weeks
    month_days = cal.monthdayscalendar(year, month)
    calendar_weeks = []
    for week in month_days:
        week_data = []
        for d in week:
            if d == 0:
                week_data.append(None)
            else:
                day_data = {
                    'day': d,
                    'intake_logs': days.get(d, {}).get('intake_logs', []),
                    'mood_entries': days.get(d, {}).get('mood_entries', []),
                    'appointments': days.get(d, {}).get('appointments', []),
                }
                week_data.append(day_data)
        calendar_weeks.append(week_data)
    return render(request, 'calendar.html', {'calendar_weeks': calendar_weeks})

@login_required
def caregiver_dashboard(request):
    if not hasattr(request.user, 'role') or request.user.role != 'caregiver':
        return redirect('meds_list')
    User = get_user_model()
    patients = User.objects.filter(role='patient')
    for patient in patients:
        # Attach missed logs in the last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        patient.missed_logs = patient.intake_logs.filter(missed=True, scheduled_time__gte=week_ago)
    return render(request, 'caregiver_dashboard.html', {'patients': patients})

@login_required
def pdf_history(request):
    intake_logs = MedicationIntakeLog.objects.filter(user=request.user).order_by('-scheduled_time')  # type: ignore
    return render(request, 'pdf_history.html', {'pdfs': intake_logs})

@login_required
def pdf_download(request):
    from datetime import date
    import calendar
    from django.template.loader import render_to_string
    from weasyprint import HTML
    from django.http import HttpResponse

    today = date.today()
    year = today.year
    month = today.month
    cal = calendar.Calendar()
    month_logs = MedicationIntakeLog.objects.filter(user=request.user, scheduled_time__year=year, scheduled_time__month=month)
    month_moods = MoodTracker.objects.filter(user=request.user, date__year=year, date__month=month)
    month_appts = Appointment.objects.filter(user=request.user, date__year=year, date__month=month)
    days = {}
    for log in month_logs:
        d = log.scheduled_time.day
        days.setdefault(d, {'intake_logs': [], 'mood_entries': [], 'appointments': []})
        days[d]['intake_logs'].append(log)
    for mood in month_moods:
        d = mood.date.day
        days.setdefault(d, {'intake_logs': [], 'mood_entries': [], 'appointments': []})
        days[d]['mood_entries'].append(mood)
    for appt in month_appts:
        d = appt.date.day
        days.setdefault(d, {'intake_logs': [], 'mood_entries': [], 'appointments': []})
        days[d]['appointments'].append(appt)
    month_days = cal.monthdayscalendar(year, month)
    calendar_weeks = []
    for week in month_days:
        week_data = []
        for d in week:
            if d == 0:
                week_data.append(None)
            else:
                day_data = {
                    'day': d,
                    'intake_logs': days.get(d, {}).get('intake_logs', []),
                    'mood_entries': days.get(d, {}).get('mood_entries', []),
                    'appointments': days.get(d, {}).get('appointments', []),
                }
                week_data.append(day_data)
        calendar_weeks.append(week_data)
    html_string = render_to_string('calendar.html', {'calendar_weeks': calendar_weeks, 'user': request.user, 'pdf_mode': True})
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="calendar.pdf"'
    return response

@login_required
def test_web_push(request):
    """Test web push notification"""
    from MedReminder.Meds.tasks import send_test_push
    send_test_push.delay(request.user.id)
    return HttpResponse("Test push notification triggered")

def home_view(request):
    return render(request, 'home.html')