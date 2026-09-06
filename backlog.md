# Backlog — Household Chores Tool (Django)

A small, ordered backlog for building a shared household chore manager on the existing `household_chores` project and `chores` app.

## Tasks

1. **Define data models** — Create `Chore`, `HouseholdMember`, and `ChoreAssignment` models in `chores/models.py` (name, description, due date, assignee, completion status).

2. **Run database migrations** — Generate and apply initial migrations so the models are stored in SQLite.

3. **Register models in Django admin** — Expose chores, members, and assignments in the admin site for quick data entry and testing.

4. **Build chore list view** — Add a URL, view, and template that lists all chores with their assignee and status.

5. **Add create/edit chore forms** — Use Django forms (or ModelForm) so users can add and update chores from the browser.

6. **Implement chore assignment** — Allow assigning a chore to a household member and reassigning when needed.

7. **Mark chores complete** — Add an action or endpoint to toggle completion status and record when a chore was done.

8. **Add basic styling** — Apply simple CSS so the chore list and forms are readable on desktop and mobile.

9. **Write unit tests** — Cover model behavior, views, and the mark-complete flow with Django’s test client.

10. **Add user authentication (stretch)** — Tie household members to Django users and restrict edits to logged-in members.
