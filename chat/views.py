from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
import json

# from config import settings
from chat.manual_backend.services import generate_response
from .models import Conversation, Message
from .file_upload import save_uploaded_file
from chat.manual_backend.ingestion import ingest_document


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
    
    # 5. save user message
    Message.objects.create(conversation=conversation, role="user", content=message)

    # 6. sent message to model and return model's reply
    try:
        reply = generate_response(message, previous_message)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=502)

    # 7 now save model response
    Message.objects.create(conversation=conversation, role="assistant", content=reply)

    return JsonResponse({"message": reply, "conversation_id": conversation.id})


# 7.4 File Upload & RAG Integration (automatic ingestion)
@csrf_exempt
@require_POST
def upload_api(request):
    uploaded_file = request.FILES.get("file")
    if not uploaded_file: return JsonResponse({"error": "File is missing"}, status=400)

    file_info = None

    try:
        # validate and save uploaded file
        file_info = save_uploaded_file(uploaded_file)

        # automatically run the RAG ingestion pipeline
        ingestion_result = ingest_document(
            file_path=file_info["absolute_path"],
            original_name=file_info["original_name"]
        )
    except ValueError as exc:   # handling expected input/data issues 
        # remove saved file if ingestion failed
        if file_info:
            default_storage.delete(file_info["stored_name"])
        return JsonResponse({"error": str(exc)}, status=400)

    except Exception as exc:   # handling other unexpected errors
        if file_info:
            default_storage.delete(file_info["stored_name"])
        return JsonResponse({"error": str(exc)}, status=500)

    return JsonResponse({
        "message": "File uploaded and indexed successfully",
        "files": {
            "name": file_info["original_name"],
            "size": file_info["size"],
            "chunks": ingestion_result["stored_count"]
        }
    }, status=201)



# # 7.4 File Upload & RAG Integration (backend upload handling)
# @csrf_exempt
# @require_POST
# def upload_api(request):
#     uploaded_file = request.FILES.get("file")
#     if not uploaded_file: return JsonResponse({"error": "File is missing"}, status=400)

#     try:
#         file_info = save_uploaded_file(uploaded_file)
#     except ValueError as exc:
#         return JsonResponse({"error": str(exc)}, status=400)

#     return JsonResponse({
#         "message": "File uploaded successfully",
#         "files": {
#             "name": file_info["original_name"],
#             "size": file_info["size"]
#         }
#     }, status=201)

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
