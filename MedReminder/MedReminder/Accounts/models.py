from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    PATIENT = 'patient'
    CAREGIVER = 'caregiver'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (PATIENT, 'Patient'),
        (CAREGIVER, 'Caregiver'),
        (ADMIN, 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=PATIENT)
    phone = models.CharField(max_length=20, blank=True, null=True)
    geofencing_enabled = models.BooleanField(default=True)
    # Add more profile fields as needed

    def __str__(self):
        return f"{self.username} ({self.role})" 