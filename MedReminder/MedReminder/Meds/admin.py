from django.contrib import admin
from .models import Medication, MedicationSchedule, MedicationIntakeLog, Inventory, MoodTracker, Appointment

admin.site.register(Medication)
admin.site.register(MedicationSchedule)
admin.site.register(MedicationIntakeLog)
admin.site.register(Inventory)
admin.site.register(MoodTracker)
admin.site.register(Appointment) 