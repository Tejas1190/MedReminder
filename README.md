# 🩺 Smart Medication Reminder System

A full-stack Django/PostgreSQL PWA for medication reminders, caregiver dashboards, geofencing, push/SMS notifications, and more.

## Features
- Add, edit, delete medications
- Schedule daily reminders
- Confirm intake with a button
- Responsive UI (desktop + mobile)
- Caregiver dashboard
- Caregiver can edit med schedules remotely
- Separate logins for caregiver, patient, admin
- Daily logs, calendar view, mood tracker
- Push notifications (browser/mobile, fallback to SMS)
- Panic/SOS button for patient
- Alerts for repeated missed doses
- Geofencing for wandering detection
- PDF download of med history
- Doctor appointment tracker
- Meds inventory reminder
- Simple PWA install
- AI chatbot for help

## Tech Stack
- Django, PostgreSQL, Celery, Twilio, ChatterBot, WeasyPrint, Bootstrap, Google Maps API

## Local Setup (Windows)

### 1. Install Requirements
- Python 3.10+
- PostgreSQL (download from https://www.postgresql.org/download/)
- Node.js (for PWA/service worker if needed)

### 2. Clone the Repo & Set Up Virtualenv
```
git clone <repo-url>
cd MedReminderExp
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure PostgreSQL
- Create a database `medreminder_db` and user `postgres` (or update credentials in `settings.py`)

### 4. Set Environment Variables (optional)
- Create a `.env` file in the project root for Twilio/Google Maps keys if needed

### 5. Run Migrations
```
cd MedReminder
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```
python manage.py createsuperuser
```

### 7. Start Celery Worker (in a new terminal)
```
celery -A MedReminder worker -l info
```

### 8. Run the Server
```
python manage.py runserver
```

### 9. Access the App
- Open http://localhost:8000/
- Admin: http://localhost:8000/admin/

### 10. For PWA
- Open in Chrome, "Add to Home Screen"

### 11. For Push Notifications
- Allow notifications in browser/mobile

### 12. Twilio/Google Maps
- Add your API keys in `.env` or `settings.py` as needed

---

**For any issues, check the README or contact the maintainer.** 