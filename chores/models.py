from django.db import models
from django.utils import timezone


class HouseholdMember(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Chore(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date", "name"]

    def __str__(self):
        return self.name

    @property
    def current_assignment(self):
        return self.assignments.order_by("-assigned_at").first()


class ChoreAssignment(models.Model):
    chore = models.ForeignKey(
        Chore,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    assignee = models.ForeignKey(
        HouseholdMember,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-assigned_at"]

    def __str__(self):
        status = "complete" if self.is_complete else "pending"
        return f"{self.chore.name} → {self.assignee.name} ({status})"

    def mark_complete(self):
        self.is_complete = True
        self.completed_at = timezone.now()
        self.save(update_fields=["is_complete", "completed_at"])

    def mark_incomplete(self):
        self.is_complete = False
        self.completed_at = None
        self.save(update_fields=["is_complete", "completed_at"])

    def toggle_complete(self):
        if self.is_complete:
            self.mark_incomplete()
        else:
            self.mark_complete()
