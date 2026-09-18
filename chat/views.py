from django.shortcuts import render
from django.http import JsonResponse

# 3.2 Backend
def chat_page(request):
    return render(request, "chat.html")

def chat_api(request):
    return JsonResponse({"message": "You said something"})