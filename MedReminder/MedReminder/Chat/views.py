from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import ChatMessage
from django.contrib.auth import get_user_model
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_MODEL = os.environ.get('GROQ_MODEL', 'mixtral-8x7b-32768')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'

def get_groq_response(user_message):
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': GROQ_MODEL,
        'messages': [
            {'role': 'user', 'content': user_message}
        ],
        'max_tokens': 256,
        'temperature': 0.7,
    }
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print('Groq API error:', response.status_code, response.text)
            return f"Groq API error: {response.status_code} - {response.text}"
    except Exception as e:
        print('Groq API exception:', str(e))
        return f"Groq API exception: {str(e)}"

@csrf_exempt
def chat_with_bot(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            user = request.user
            # Store user message
            ChatMessage.objects.create(user=user, sender=ChatMessage.USER, message=user_message)
            # Get bot response from Groq AI
            bot_response = get_groq_response(user_message)
            # Store bot message
            ChatMessage.objects.create(user=user, sender=ChatMessage.BOT, message=bot_response)
            return JsonResponse({'user': user_message, 'bot': bot_response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def chatbot_page(request):
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')  # type: ignore
    return render(request, 'chatbot.html', {'chat_history': chat_history})