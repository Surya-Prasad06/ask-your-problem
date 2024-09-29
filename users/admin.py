from django.contrib import admin
from .models import Profile, Post, Conversation, Comment, Message, Room

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(Room)
admin.site.register(Conversation)
admin.site.register(Comment)