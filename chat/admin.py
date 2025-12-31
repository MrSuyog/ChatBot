
from django.contrib import admin
from .models import Message, Profile

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "sender", "short_message", "created_at")
    list_filter = ("sender", "created_at")
    search_fields = ("user__username", "message")

    def short_message(self, obj):
        return (obj.message[:60] + "…") if len(obj.message) > 60 else obj.message

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "preferred_name", "created_at", "updated_at")
    search_fields = ("user__username", "preferred_name")