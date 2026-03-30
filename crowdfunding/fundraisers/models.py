from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Fundraiser(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal = models.IntegerField()
    image = models.URLField()
    is_open = models.BooleanField()
    is_deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_fundraisers"
    )

    def __str__(self):
        return self.title


class Pledge(models.Model):
    amount = models.IntegerField()
    comment = models.CharField(max_length=200)
    anonymous = models.BooleanField()
    is_deleted = models.BooleanField(default=False)

    fundraiser = models.ForeignKey(
        "Fundraiser",
        on_delete=models.CASCADE,
        related_name="pledges"
    )
    supporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pledges"
    )

    def __str__(self):
        return f"Pledge {self.amount} for {self.fundraiser.title}"


class FundraiserChangeLog(models.Model):
    fundraiser = models.ForeignKey(
        Fundraiser,
        on_delete=models.CASCADE,
        related_name="change_logs"
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="fundraiser_change_logs"
    )
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.fundraiser.title} | {self.field_name} | {self.changed_at}"