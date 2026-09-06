from django.contrib import admin

from .models import Chore, ChoreAssignment, HouseholdMember


@admin.register(HouseholdMember)
class HouseholdMemberAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ["name", "due_date", "created_at"]
    search_fields = ["name", "description"]


@admin.register(ChoreAssignment)
class ChoreAssignmentAdmin(admin.ModelAdmin):
    list_display = ["chore", "assignee", "is_complete", "assigned_at", "completed_at"]
    list_filter = ["is_complete"]
