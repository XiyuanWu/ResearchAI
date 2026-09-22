from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_page, name="chat"),
    path("chat/", views.chat_api, name="chat_api"),
    path("upload/", views.upload_api, name="views.upload_api")
]
