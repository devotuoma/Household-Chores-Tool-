# Household-Chores-Tool-
A tool for managing shared household chores. 



# Household Chores Tool

A small Django web app for coordinating chores in a shared household. It gives everyone a single, easy-to-read board for seeing what needs to be done, who is responsible, and whether a task is complete.

## What the application does

- Creates household members, chores, and chore assignments.
- Stores a chore name, optional description, optional due date, and creation time.
- Shows all chores in a responsive dashboard with the current assignee and status.
- Lets users add and edit chores from the browser.
- Lets users assign a chore to a household member or reassign it when responsibilities change.
- Lets users mark an assigned chore complete or return it to pending. Completion records the time it was done; returning it to pending clears that timestamp.
- Provides Django admin pages for quick management of chores, household members, and assignments.

The dashboard distinguishes pending, complete, and unassigned chores, and works on desktop and mobile-sized screens.

## Main workflows

1. Add household members through the Django admin site.
2. Create a chore from the **Add chore** action.
3. Assign the chore to a household member.
4. Use **Complete** when the work is done, or **Mark pending** if it needs to be reopened.
5. Edit a chore or change its assignee whenever plans change.

## Data model

| Model | Purpose |
| --- | --- |
| `HouseholdMember` | A person in the household who can be assigned chores. |
| `Chore` | A task with a name, description, optional due date, and creation time. |
| `ChoreAssignment` | Connects a chore to its current assignee and stores completion state, completion time, and assignment time. |

Assignments are ordered by their assignment time, so the most recent assignment is used as a chore’s current assignee.

## Routes

| URL | Purpose |
| --- | --- |
| `/` | Chore dashboard |
| `/new/` | Create a chore |
| `/<chore-id>/edit/` | Edit a chore |
| `/<chore-id>/assign/` | Assign or reassign a chore |
| `/admin/` | Django administration site |

## Getting started

This project uses Python 3.11+ and Django 5.2.

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Then open <http://127.0.0.1:8000/>. To use the admin site, create an administrator account first:

```bash
uv run python manage.py createsuperuser
```

## Tests

The test suite covers model behavior, ordering and cascade deletion, admin registration, chore list states, valid and invalid form submissions, assignment and reassignment, not-found responses, and the POST-only complete/pending flow.

Run it with:

```bash
uv run python manage.py test
```

## Planned stretch feature

Authentication is the remaining stretch goal: link household members to Django user accounts and limit edits to signed-in members.
