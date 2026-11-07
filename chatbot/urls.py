"""
Chatbot URLs
"""
from django.urls import path
from . import views, api_views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('send/', views.send_message, name='send_message'),
    path('clear/', views.clear_history, name='clear_history'),
    path('api/query/', api_views.chatbot_query_api, name='query_api'),
]

