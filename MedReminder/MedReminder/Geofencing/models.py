from django.db import models
from django.conf import settings

class GeofenceZone(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='geofences')
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius_meters = models.PositiveIntegerField(default=100)  # type: ignore
    active = models.BooleanField(default=True)  # type: ignore

    def __str__(self):
        return f"{self.name} ({self.user.username})"  # type: ignore

class SOSAlert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sos_alerts')
    triggered_at = models.DateTimeField(auto_now_add=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    resolved = models.BooleanField(default=False)  # type: ignore
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"SOS by {self.user.username} at {self.triggered_at}"  # type: ignore 