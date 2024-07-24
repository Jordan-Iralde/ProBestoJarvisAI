from django.urls import path
from .views import handle_query, handle_voice_cloning, handle_face_recognition

urlpatterns = [
    path('api/query/', handle_query, name='handle_query'),
    path('api/voice-clone/', handle_voice_cloning, name='handle_voice_cloning'),
    path('api/face-recognize/', handle_face_recognition, name='handle_face_recognition'),
]
