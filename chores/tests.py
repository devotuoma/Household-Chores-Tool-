from datetime import date

from django.contrib import admin
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Chore, ChoreAssignment, HouseholdMember


class HouseholdMemberModelTests(TestCase):
    def test_str_returns_name(self):
        member = HouseholdMember.objects.create(name="Alex")
        self.assertEqual(str(member), "Alex")

    def test_members_are_ordered_alphabetically(self):
        HouseholdMember.objects.create(name="Sam")
        HouseholdMember.objects.create(name="Alex")

        self.assertEqual(list(HouseholdMember.objects.values_list("name", flat=True)), ["Alex", "Sam"])


class ChoreModelTests(TestCase):
    def test_str_returns_name(self):
        chore = Chore.objects.create(name="Vacuum living room")
        self.assertEqual(str(chore), "Vacuum living room")

    def test_current_assignment_returns_latest(self):
        chore = Chore.objects.create(name="Dishes")
        member_a = HouseholdMember.objects.create(name="Alex")
        member_b = HouseholdMember.objects.create(name="Sam")

        older = ChoreAssignment.objects.create(chore=chore, assignee=member_a)
        newer = ChoreAssignment.objects.create(chore=chore, assignee=member_b)

        ChoreAssignment.objects.filter(pk=older.pk).update(
            assigned_at=timezone.now() - timezone.timedelta(days=1)
        )

        self.assertEqual(chore.current_assignment, newer)


class ChoreAssignmentModelTests(TestCase):
    def setUp(self):
        self.member = HouseholdMember.objects.create(name="Alex")
        self.chore = Chore.objects.create(name="Take out trash")

    def test_defaults_to_pending(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.chore,
            assignee=self.member,
        )
        self.assertFalse(assignment.is_complete)
        self.assertIsNone(assignment.completed_at)

    def test_str_shows_pending_status(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.chore,
            assignee=self.member,
        )
        self.assertIn("pending", str(assignment))

    def test_mark_complete_sets_timestamp(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.chore,
            assignee=self.member,
        )
        assignment.mark_complete()
        assignment.refresh_from_db()

        self.assertTrue(assignment.is_complete)
        self.assertIsNotNone(assignment.completed_at)

    def test_mark_incomplete_clears_timestamp(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.chore,
            assignee=self.member,
            is_complete=True,
            completed_at=timezone.now(),
        )
        assignment.mark_incomplete()
        assignment.refresh_from_db()

        self.assertFalse(assignment.is_complete)
        self.assertIsNone(assignment.completed_at)

    def test_toggle_complete_switches_state(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.chore,
            assignee=self.member,
        )
        assignment.toggle_complete()
        assignment.refresh_from_db()
        self.assertTrue(assignment.is_complete)

        assignment.toggle_complete()
        assignment.refresh_from_db()
        self.assertFalse(assignment.is_complete)

    def test_deleting_chore_deletes_assignments(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.chore,
            assignee=self.member,
        )
        assignment_id = assignment.pk
        self.chore.delete()
        self.assertFalse(ChoreAssignment.objects.filter(pk=assignment_id).exists())

    def test_deleting_member_deletes_assignments(self):
        assignment = ChoreAssignment.objects.create(chore=self.chore, assignee=self.member)

        self.member.delete()

        self.assertFalse(ChoreAssignment.objects.filter(pk=assignment.pk).exists())


class AdminRegistrationTests(TestCase):
    def test_all_chore_models_are_registered(self):
        for model in (Chore, HouseholdMember, ChoreAssignment):
            self.assertTrue(admin.site.is_registered(model))


class ChoreListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.member = HouseholdMember.objects.create(name="Alex")
        self.chore = Chore.objects.create(
            name="Vacuum",
            due_date=date(2026, 9, 10),
        )
        ChoreAssignment.objects.create(chore=self.chore, assignee=self.member)

    def test_list_page_loads(self):
        response = self.client.get(reverse("chore_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vacuum")
        self.assertContains(response, "Alex")
        self.assertContains(response, "Pending")

    def test_empty_list_explains_how_to_start(self):
        Chore.objects.all().delete()

        response = self.client.get(reverse("chore_list"))

        self.assertContains(response, "No chores yet. Add the first one")


class ChoreFormViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_chore(self):
        response = self.client.post(
            reverse("chore_create"),
            {
                "name": "Mop kitchen",
                "description": "Use the new mop",
                "due_date": "2026-09-12",
            },
        )
        self.assertRedirects(response, reverse("chore_list"))
        self.assertTrue(Chore.objects.filter(name="Mop kitchen").exists())

    def test_edit_chore(self):
        chore = Chore.objects.create(name="Old name")
        response = self.client.post(
            reverse("chore_edit", args=[chore.pk]),
            {
                "name": "Updated name",
                "description": "",
                "due_date": "",
            },
        )
        self.assertRedirects(response, reverse("chore_list"))
        chore.refresh_from_db()
        self.assertEqual(chore.name, "Updated name")

    def test_invalid_create_shows_error_and_does_not_save(self):
        response = self.client.post(
            reverse("chore_create"),
            {"name": "", "description": "", "due_date": "not-a-date"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Chore.objects.count(), 0)

    def test_invalid_edit_does_not_overwrite_existing_chore(self):
        chore = Chore.objects.create(name="Keep this name")

        response = self.client.post(
            reverse("chore_edit", args=[chore.pk]),
            {"name": "", "description": "", "due_date": ""},
        )

        self.assertEqual(response.status_code, 200)
        chore.refresh_from_db()
        self.assertEqual(chore.name, "Keep this name")


class AssignmentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.member = HouseholdMember.objects.create(name="Alex")
        self.other_member = HouseholdMember.objects.create(name="Sam")
        self.chore = Chore.objects.create(name="Laundry")

    def test_assign_chore_creates_assignment(self):
        response = self.client.post(
            reverse("assign_chore", args=[self.chore.pk]),
            {"assignee": self.member.pk},
        )
        self.assertRedirects(response, reverse("chore_list"))
        assignment = self.chore.current_assignment
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment.assignee, self.member)

    def test_reassign_chore_updates_assignee(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.chore,
            assignee=self.member,
        )
        response = self.client.post(
            reverse("assign_chore", args=[self.chore.pk]),
            {"assignee": self.other_member.pk},
        )
        self.assertRedirects(response, reverse("chore_list"))
        assignment.refresh_from_db()
        self.assertEqual(assignment.assignee, self.other_member)

    def test_invalid_assignment_does_not_create_assignment(self):
        response = self.client.post(
            reverse("assign_chore", args=[self.chore.pk]),
            {"assignee": "99999"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice")
        self.assertFalse(ChoreAssignment.objects.filter(chore=self.chore).exists())

    def test_assigning_unknown_chore_returns_not_found(self):
        response = self.client.get(reverse("assign_chore", args=[99999]))

        self.assertEqual(response.status_code, 404)


class MarkCompleteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.member = HouseholdMember.objects.create(name="Alex")
        self.chore = Chore.objects.create(name="Clean bathroom")
        self.assignment = ChoreAssignment.objects.create(
            chore=self.chore,
            assignee=self.member,
        )

    def test_mark_complete_via_post(self):
        response = self.client.post(
            reverse("mark_complete", args=[self.assignment.pk]),
        )
        self.assertRedirects(response, reverse("chore_list"))
        self.assignment.refresh_from_db()
        self.assertTrue(self.assignment.is_complete)
        self.assertIsNotNone(self.assignment.completed_at)

    def test_mark_complete_requires_post(self):
        response = self.client.get(reverse("mark_complete", args=[self.assignment.pk]))
        self.assertEqual(response.status_code, 405)
        self.assignment.refresh_from_db()
        self.assertFalse(self.assignment.is_complete)

    def test_marking_unknown_assignment_returns_not_found(self):
        response = self.client.post(reverse("mark_complete", args=[99999]))

        self.assertEqual(response.status_code, 404)

    def test_toggle_back_to_pending(self):
        self.assignment.mark_complete()
        response = self.client.post(
            reverse("mark_complete", args=[self.assignment.pk]),
        )
        self.assertRedirects(response, reverse("chore_list"))
        self.assignment.refresh_from_db()
        self.assertFalse(self.assignment.is_complete)
        self.assertIsNone(self.assignment.completed_at)
