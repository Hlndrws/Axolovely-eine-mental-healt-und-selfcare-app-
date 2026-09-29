from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from ..forms import RoutineForm
from ..models import Routine, RoutineCompletion


class RoutinesView(LoginRequiredMixin, View):
    template_name = "routines.html"
    login_url = "login"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_page_context())

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        routine_id = self.get_routine_id(request)

        if action == "add":
            self.add_routine(request)
        elif action == "toggle":
            self.toggle_routine(routine_id)
        elif action == "delete":
            self.delete_routine(routine_id)
        return redirect("routines")

    def get_routine_id(self, request):
        try:
            return int(request.POST.get("routine_id", ""))
        except (TypeError, ValueError):
            return None

    def add_routine(self, request):
        form = RoutineForm(request.POST)
        if form.is_valid():
            routine = form.save(commit=False)
            routine.user = request.user
            routine.save()
            messages.success(request, "Routine hinzugefügt.")
        else:
            messages.error(request, "Bitte gib einen Namen mit höchstens 100 Zeichen ein.")

    def toggle_routine(self, routine_id):
        routine = Routine.objects.filter(pk=routine_id, user=self.request.user).first() if routine_id else None
        if not routine:
            return

        today = timezone.localdate()
        if routine.frequency == "weekly":
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            weekly_completions = RoutineCompletion.objects.filter(
                routine=routine,
                date__range=(week_start, week_end),
            )
            if weekly_completions.exists():
                weekly_completions.delete()
            else:
                RoutineCompletion.objects.create(routine=routine, date=today)
            return

        completion, created = RoutineCompletion.objects.get_or_create(
            routine=routine,
            date=today,
        )
        if not created:
            completion.delete()

    def delete_routine(self, routine_id):
        Routine.objects.filter(pk=routine_id, user=self.request.user).delete()
        messages.success(self.request, "Routine entfernt.")

    def get_page_context(self):
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        daily_completed_ids = set(
            RoutineCompletion.objects.filter(date=today, routine__user=self.request.user)
            .values_list("routine_id", flat=True)
        )
        weekly_completed_ids = set(
            RoutineCompletion.objects.filter(
                date__range=(week_start, week_end),
                routine__user=self.request.user,
            )
            .values_list("routine_id", flat=True)
        )
        daily_rows = []
        weekly_rows = []
        for routine in Routine.objects.filter(user=self.request.user):
            row = {"routine": routine}
            if routine.frequency == "weekly":
                row["completed"] = routine.id in weekly_completed_ids
                weekly_rows.append(row)
            else:
                row["completed"] = routine.id in daily_completed_ids
                daily_rows.append(row)

        daily_completed_count = sum(row["completed"] for row in daily_rows)
        weekly_completed_count = sum(row["completed"] for row in weekly_rows)
        return {
            "today": today,
            "daily_rows": daily_rows,
            "weekly_rows": weekly_rows,
            "form": RoutineForm(),
            "daily_completed_count": daily_completed_count,
            "daily_total_count": len(daily_rows),
            "weekly_completed_count": weekly_completed_count,
            "weekly_total_count": len(weekly_rows),
        }