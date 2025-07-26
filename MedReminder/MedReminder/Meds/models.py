from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

class Medication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    inventory_count = models.PositiveIntegerField(default=0)
    inventory_threshold = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class MedicationSchedule(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='schedules')
    time = models.TimeField()
    days_of_week = models.CharField(max_length=20, default='daily')  # e.g., 'Mon,Tue,Wed' or 'daily'
    caregiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='caregiver_schedules')

    def __str__(self):
        return f"{self.medication.name} at {self.time} ({self.days_of_week})"

class MedicationIntakeLog(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='intake_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='intake_logs')
    scheduled_time = models.DateTimeField()
    taken = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    missed = models.BooleanField(default=False)
    mood = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.medication.name} for {self.user.username} at {self.scheduled_time}"

class Inventory(models.Model):
    medication = models.OneToOneField(Medication, on_delete=models.CASCADE, related_name='inventory')
    count = models.PositiveIntegerField(default=0)
    threshold = models.PositiveIntegerField(default=5)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inventory for {self.medication.name}: {self.count}"

class MoodTracker(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mood_entries')
    date = models.DateField()
    mood = models.PositiveSmallIntegerField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.mood}"

class WebPushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.TextField()
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} subscription"

class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    doctor_name = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment with {self.doctor_name} on {self.date} at {self.time} for {self.user.username}"