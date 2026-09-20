from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

# from config import settings
from .services import generate_response
from .models import Conversation, Message

# 3.2 Backend
def chat_page(request):
    return render(request, "chat.html")

# 5.2 Conversation Memory (load previous message)
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
    
    # 3. get or create conversation
    conversation_id = data.get("conversation_id")
    if conversation_id:
        try: 
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return JsonResponse({"error": "Conversation not found"}, status=404)
    else:
        conversation = Conversation.objects.create(title=message[:50] or "new chat")

    # 4. load previous message (before saving the new one)
    previous_message = list(conversation.messages.order_by("created_at").values("role", "content"))
    
    #. 5. save user message
    Message.objects.create(conversation=conversation, role="user", content=message)

    # 6. sent message to model and return model's reply
    try:
        reply = generate_response(message)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=502)

    # 7 now save model response
    Message.objects.create(conversation=conversation, role="assistant", content=reply)

    return JsonResponse({"message": reply, "conversation_id": conversation.id})


# # 5.1 Chat Storage (save chat history)
# @csrf_exempt
# @require_POST
# def chat_api(request):
#     # 1. read json data and convert to dict
#     try: 
#         data = json.loads(request.body.decode("utf-8") or "{}")
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Invalid JSON"}, status=400)

#     # 2. get the plain text input from the user
#     message = (data.get("message") or "").strip()
#     if not message: 
#         return JsonResponse({"error": "Message is missing"}, status=400)
    
#     # 2.5. create new conversation and save user input
#     conversation = Conversation.objects.create(title=message[:50] or "new chat")
#     Message.objects.create(conversation=conversation, role="user", content=message)

#     # 3. sent message to model and return model's reply
#     try:
#         reply = generate_response(message)
#     except Exception as exc:
#         return JsonResponse({"error": str(exc)}, status=502)

#     # 3.5 now save model response
#     Message.objects.create(conversation=conversation, role="assistant", content=reply)

#     return JsonResponse({"message": reply})


# # 4.2 LLM Interaction (return response to frontend)
# @csrf_exempt
# @require_POST
# def chat_api(request):
#     # 1. read json data and convert to dict
#     try: 
#         data = json.loads(request.body.decode("utf-8") or "{}")
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Invalid JSON"}, status=400)

#     # 2. get the plain text input from the user
#     message = (data.get("message") or "").strip()
#     if not message: 
#         return JsonResponse({"error": "Message is missing"}, status=400)
    
#     # 3. sent message to model and return model's reply
#     try:
#         reply = generate_response(message)
#     except Exception as exc:
#         return JsonResponse({"error": str(exc)}, status=502)

#     return JsonResponse({"message": reply})


# # 3.3 Connect App
# @csrf_exempt
# @require_POST
# def chat_api(request):
#     data = json.loads(request.body)
#     message = data.get("message", "")
#     return JsonResponse({"message": f"You said {message}. "})
