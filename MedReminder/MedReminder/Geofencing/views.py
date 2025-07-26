from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GeofenceZone
from django.utils import timezone
from django.conf import settings

# SOS functionality removed

@login_required
def geofencing_page(request):
    geofences = GeofenceZone.objects.filter(user=request.user)  # type: ignore
    return render(request, 'geofencing.html', {'geofences': geofences, 'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY})

@login_required
def geofencing_add(request):
    if request.method == 'POST':
        GeofenceZone.objects.create(
            user=request.user,
            name=request.POST['name'],
            latitude=request.POST['latitude'],
            longitude=request.POST['longitude'],
            radius_meters=request.POST['radius_meters'],
            active=True
        )  # type: ignore
    return redirect('geofencing:geofencing_page')

@login_required
def geofencing_delete(request, zone_id):
    zone = get_object_or_404(GeofenceZone, id=zone_id, user=request.user)
    if request.method == 'POST':
        zone.delete()
    return redirect('geofencing:geofencing_page')

@login_required
def toggle_geofencing(request):
    user = request.user
    user.geofencing_enabled = not user.geofencing_enabled
    user.save()
    return redirect('geofencing:geofencing_page')
