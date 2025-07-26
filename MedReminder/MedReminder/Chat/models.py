from django.db import models
from django.conf import settings

class ChatMessage(models.Model):
    USER = 'user'
    BOT = 'bot'
    SENDER_CHOICES = [
        (USER, 'User'),
        (BOT, 'Bot'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} at {self.timestamp}: {str(self.message)[:30]}"  # type: ignore 