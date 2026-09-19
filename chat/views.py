from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

# from config import settings
from .services import generate_response

# 3.2 Backend
def chat_page(request):
    return render(request, "chat.html")

# 4.2 LLM Interaction (return response to frontend)
@csrf_exempt
@require_POST
def chat_api(request):
    # 1. read json data and convert to dict
    try: 
        data = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # 2. get the plain text input from the user
    message = (data.get("message") or "").strip()
    if not message: 
        return JsonResponse({"error": "Message is missing"}, status=400)
    
    # 3. sent message to model and return model's reply
    try:
        reply = generate_response(message)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=502)

    return JsonResponse({"message": reply})


# # 3.3 Connect App
# @csrf_exempt
# @require_POST
# def chat_api(request):
#     data = json.loads(request.body)
#     message = data.get("message", "")
#     return JsonResponse({"message": f"You said {message}. "})
