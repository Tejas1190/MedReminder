from celery import shared_task
from django.utils import timezone
from django.conf import settings
from .models import MedicationSchedule, MedicationIntakeLog, WebPushSubscription
from pywebpush import webpush, WebPushException
from django.contrib.auth import get_user_model
from datetime import timedelta

import logging
import json

logger = logging.getLogger(__name__)

@shared_task
def send_med_reminder(medication_schedule_id):
    logger.info(f"Starting send_med_reminder for schedule {medication_schedule_id}")
    try:
        schedule = MedicationSchedule.objects.get(id=medication_schedule_id)
        user = schedule.user
        medication = schedule.medication
        logger.info(f"Sending reminder for {medication.name} to user {user.username}")
        
        # Create intake log
        log = MedicationIntakeLog.objects.create(
            user=user,
            medication=medication,
            scheduled_time=timezone.now(),
            taken=False
        )
        logger.info(f"Created intake log {log.id}")
        
        # SMS sending removed (Fast2SMS deprecated)
        if user.phone:
            pass  # No SMS logic
        else:
            logger.warning(f"No phone number for user {user.username}")
        
        # Send web push notification
        subscriptions = WebPushSubscription.objects.filter(user=user)
        logger.info(f"Found {subscriptions.count()} web push subscriptions for {user.username}")
        for sub in subscriptions:
            try:
                payload = {
                    'title': 'MedReminder',
                    'body': f"Take {medication.name}, {medication.dosage}",
                    'data': {
                        'log_id': log.id,
                        'url': f"/confirm-intake/?log_id={log.id}"
                    }
                }
                webpush(
                    subscription_info={
                        'endpoint': sub.endpoint,
                        'keys': {
                            'p256dh': sub.p256dh,
                            'auth': sub.auth
                        }
                    },
                    data=json.dumps(payload),
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={
                        'sub': f'mailto:{settings.VAPID_ADMIN_EMAIL}'
                    }
                )
                logger.info(f"Web push sent to {user.username}")
            except WebPushException as e:
                logger.error(f"Failed to send web push to {user.username}: {str(e)}")
        
        # Schedule the confirmation notification 10 minutes later
        from .tasks import send_confirmation_reminder
        eta = timezone.now() + timedelta(minutes=10)
        logger.info(f"Scheduling confirmation reminder for log {log.id} at {eta}")
        send_confirmation_reminder.apply_async(args=[log.id], eta=eta)
        
    except MedicationSchedule.DoesNotExist:
        logger.error(f"MedicationSchedule with id {medication_schedule_id} does not exist")

@shared_task
def send_test_push(user_id):
    from django.contrib.auth import get_user_model
    from .models import WebPushSubscription
    User = get_user_model()
    user = User.objects.get(id=user_id)
    
    subscriptions = WebPushSubscription.objects.filter(user=user)
    for sub in subscriptions:
        try:
            payload = {
                'title': 'Test Notification',
                'body': 'This is a test push from MedReminder!',
                'data': {'url': '/'}
            }
            webpush(
                subscription_info={
                    'endpoint': sub.endpoint,
                    'keys': {'p256dh': sub.p256dh, 'auth': sub.auth}
                },
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={'sub': f'mailto:{settings.VAPID_ADMIN_EMAIL}'}
            )
            logger.info(f"Test push sent to {user.username}")
        except Exception as e:
            logger.error(f"Test push failed: {str(e)}")

@shared_task
def check_missed_doses():
    User = get_user_model()
    caregivers = User.objects.filter(role='caregiver')  # type: ignore
    week_ago = timezone.now() - timedelta(days=7)
    for caregiver in caregivers:
        patients = User.objects.filter(role='patient')  # type: ignore
        for patient in patients:
            missed_logs = MedicationIntakeLog.objects.filter(user=patient, missed=True, scheduled_time__gte=week_ago)  # type: ignore
            if missed_logs.count() >= 3:
                message = f"Alert: {patient.username} has missed {missed_logs.count()} doses in the last 7 days."
                print(f"Would send web push to {caregiver}: {message}")
                # Removed Twilio code
