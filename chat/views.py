from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

# 3.2 Backend
def chat_page(request):
    return render(request, "chat.html")


# 3.3 Connect App
@csrf_exempt
@require_POST
def chat_api(request):
    data = json.loads(request.body)
    message = data.get("message", "")
    return JsonResponse({"message": f"You said {message}. "})
