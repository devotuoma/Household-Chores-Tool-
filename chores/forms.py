from django import forms

from .models import Chore, ChoreAssignment, HouseholdMember


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ["name", "description", "due_date"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = ChoreAssignment
        fields = ["assignee"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignee"].queryset = HouseholdMember.objects.order_by("name")
