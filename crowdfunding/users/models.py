from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):

    def __str__(self):
        return self.username

# for admin interface

class UserChangeLog(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="change_logs"
    )
    changed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="admin_changed_user_logs"
    )
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.user.username} | {self.field_name} | {self.changed_at}"
    
# for admin interface