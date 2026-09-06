from django.urls import path

from . import views

urlpatterns = [
    path("", views.chore_list, name="chore_list"),
    path("new/", views.chore_create, name="chore_create"),
    path("<int:pk>/edit/", views.chore_edit, name="chore_edit"),
    path("<int:pk>/assign/", views.assign_chore, name="assign_chore"),
    path("assignments/<int:pk>/toggle/", views.mark_complete, name="mark_complete"),
]
