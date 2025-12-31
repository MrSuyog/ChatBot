
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    preferred_name = models.CharField(max_length=80, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = self.preferred_name or self.user.get_full_name() or self.user.username
        return f"{self.user.username} → {name}"

class Message(models.Model):
    USER = "user"
    BOT = "bot"
    SENDER_CHOICES = [(USER, "user"), (BOT, "bot")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=4, choices=SENDER_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        indexes = [models.Index(fields=["user", "id"])]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} [{self.sender}] {self.message[:30]}"

    def as_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "message": self.message,
            "timestamp": self.created_at.isoformat(),
        }