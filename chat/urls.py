
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    re_path(r'^api/history/?$', views.api_history, name='api_history'),
    re_path(r'^api/messages/?$', views.api_messages, name='api_messages'),
    re_path(r'^api/send/?$', views.api_send, name='api_send'),
]