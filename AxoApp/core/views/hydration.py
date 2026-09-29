from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from ..forms import HydrationGoalForm
from ..models import HydrationDay


class HydrationView(LoginRequiredMixin, View):
    template_name = "hydration.html"
    login_url = "login"

    def get(self, request, *args, **kwargs):
        hydration_day = self.get_today_record()
        form = HydrationGoalForm(initial={
            "goal_liters": hydration_day.goal_ml / 1000,
        })
        return self.render_page(hydration_day, form)

    def post(self, request, *args, **kwargs):
        hydration_day = self.get_today_record()
        action = request.POST.get("action")

        if action == "toggle_glass":
            try:
                glass_number = int(request.POST.get("glass_number", ""))
            except (TypeError, ValueError):
                return redirect("hydration")

            filled_glasses = hydration_day.consumed_ml // 250
            if glass_number == filled_glasses + 1:
                HydrationDay.objects.filter(pk=hydration_day.pk).update(
                    consumed_ml=F("consumed_ml") + 250,
                )
            elif glass_number == filled_glasses and filled_glasses > 0:
                HydrationDay.objects.filter(pk=hydration_day.pk).update(
                    consumed_ml=F("consumed_ml") - 250,
                )
            return redirect("hydration")

        if action == "save_goal":
            form = HydrationGoalForm(request.POST)
            if form.is_valid():
                hydration_day.goal_ml = int(form.cleaned_data["goal_liters"] * 1000)
                hydration_day.save(update_fields=["goal_ml", "updated_at"])
                messages.success(request, "Dein Trinkziel für heute wurde gespeichert.")
                return redirect("hydration")
            return self.render_page(hydration_day, form)

        return redirect("hydration")

    def get_today_record(self):
        today = timezone.localdate()
        hydration_day, _ = HydrationDay.objects.get_or_create(user=self.request.user, date=today)
        return hydration_day

    def render_page(self, hydration_day, form):
        hydration_day.refresh_from_db()
        glass_count = max(
            (hydration_day.goal_ml + 249) // 250,
            hydration_day.consumed_ml // 250 + 1,
        )
        filled_glasses = hydration_day.consumed_ml // 250
        glasses = [
            {
                "number": number,
                "filled": number <= filled_glasses,
                "can_toggle": number in (filled_glasses, filled_glasses + 1) and number > 0,
            }
            for number in range(1, glass_count + 1)
        ]
        progress = min(100, round(hydration_day.consumed_ml * 100 / hydration_day.goal_ml))
        return render(self.request, self.template_name, {
            "today": hydration_day.date,
            "hydration_day": hydration_day,
            "goal_form": form,
            "glasses": glasses,
            "progress": progress,
            "goal_reached": hydration_day.consumed_ml >= hydration_day.goal_ml,
        })