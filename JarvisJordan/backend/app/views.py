from django.shortcuts import render
from django.http import JsonResponse
from .models import Query, OffensiveWord
from .utils import process_query, generate_voice, recognize_face

def handle_query(request):
    user_query = request.GET.get('query')
    response = process_query(user_query)
    Query.objects.create(user_query=user_query, response=response)
    return JsonResponse({'response': response})

def handle_voice_cloning(request):
    text = request.GET.get('text')
    audio_path = generate_voice(text)
    return JsonResponse({'audio_path': audio_path})

def handle_face_recognition(request):
    image_path = request.GET.get('image_path')
    result = recognize_face(image_path)
    return JsonResponse({'result': result})
