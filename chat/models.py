from django.db import models

# Create your models here.

# 5.1 Chat Storage (database model)
# store all conversion list
class Conversation(models.Model):
    title = models.CharField(max_length=200, default="new chat")
    created_at = models.DateTimeField(auto_now_add=True)

# store single conversation chat history
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
