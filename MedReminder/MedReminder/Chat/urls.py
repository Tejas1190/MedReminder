from django.urls import path
from .views import chat_with_bot, chatbot_page

urlpatterns = [
    path('chat/', chat_with_bot, name='chat_with_bot'),
    path('', chatbot_page, name='chatbot_page'),
] 