from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AssignmentForm, ChoreForm
from .models import Chore, ChoreAssignment


def chore_list(request):
    chores = Chore.objects.prefetch_related("assignments__assignee")
    return render(request, "chores/chore_list.html", {"chores": chores})


def chore_create(request):
    if request.method == "POST":
        form = ChoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("chore_list")
    else:
        form = ChoreForm()
    return render(request, "chores/chore_form.html", {"form": form, "title": "Add chore"})


def chore_edit(request, pk):
    chore = get_object_or_404(Chore, pk=pk)
    if request.method == "POST":
        form = ChoreForm(request.POST, instance=chore)
        if form.is_valid():
            form.save()
            return redirect("chore_list")
    else:
        form = ChoreForm(instance=chore)
    return render(request, "chores/chore_form.html", {"form": form, "title": "Edit chore"})


def assign_chore(request, pk):
    chore = get_object_or_404(Chore, pk=pk)
    assignment = chore.current_assignment

    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            if assignment:
                form.save()
            else:
                ChoreAssignment.objects.create(
                    chore=chore,
                    assignee=form.cleaned_data["assignee"],
                )
            return redirect("chore_list")
    else:
        form = AssignmentForm(instance=assignment)

    return render(
        request,
        "chores/assign_form.html",
        {"form": form, "chore": chore, "title": "Assign chore"},
    )


@require_POST
def mark_complete(request, pk):
    assignment = get_object_or_404(ChoreAssignment, pk=pk)
    assignment.toggle_complete()
    return redirect("chore_list")
