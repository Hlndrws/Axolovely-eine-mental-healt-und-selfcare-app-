from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.views import View

from ..forms import MoodEntryForm
from ..models import FocusLabel, MoodEntry
from .constants import MOOD_FACES


class MoodTrackerView(LoginRequiredMixin, View):
    template_name = "mood_tracker.html"
    login_url = "login"

    def get(self, request, *args, **kwargs):
        selected_date = self.get_selected_date(request.GET.get("date"))
        entry = MoodEntry.objects.filter(user=request.user, date=selected_date).first()
        form = MoodEntryForm(initial={
            "mood": entry.mood if entry else "",
            "note": entry.note if entry else "",
            "focus_labels": entry.focus_labels.all() if entry else [],
        }, user=request.user)
        return self.render_tracker(form, selected_date, entry)

    def post(self, request, *args, **kwargs):
        selected_date = self.get_selected_date(request.POST.get("date"))
        form = MoodEntryForm(request.POST, user=request.user)
        if form.is_valid():
            entry, _ = MoodEntry.objects.update_or_create(
                date=selected_date,
                user=request.user,
                defaults={
                    "mood": int(form.cleaned_data["mood"]),
                    "note": form.cleaned_data["note"],
                },
            )
            selected_labels = list(form.cleaned_data["focus_labels"])
            new_label_name = form.cleaned_data["new_focus_label"]
            if new_label_name and not any(
                label.name.casefold() == new_label_name.casefold()
                for label in selected_labels
            ):
                new_label, _ = FocusLabel.objects.get_or_create(
                    name=new_label_name,
                    user=request.user,
                )
                selected_labels.append(new_label)
            entry.focus_labels.set(selected_labels)
            messages.success(request, f"Dein Eintrag vom {selected_date:%d.%m.%Y} wurde gespeichert.")
            return redirect(f"{reverse('mood_tracker')}?date={selected_date.isoformat()}")

        entry = MoodEntry.objects.filter(user=request.user, date=selected_date).first()
        return self.render_tracker(form, selected_date, entry)

    def get_selected_date(self, requested_date):
        today = timezone.localdate()
        try:
            selected_date = date.fromisoformat(requested_date) if requested_date else today
        except ValueError:
            selected_date = today
        return min(selected_date, today)

    def render_tracker(self, form, selected_date, entry):
        today = timezone.localdate()
        selected_mood = form["mood"].value()
        mood_options = []
        for mood, label in MoodEntry.MOOD_CHOICES:
            image_path = f"pics/mood{mood}.png"
            mood_options.append({
                "value": mood,
                "label": label,
                "image_url": static(image_path),
                "has_image": bool(finders.find(image_path)),
                "face": MOOD_FACES[mood],
                "selected": str(selected_mood) == str(mood),
            })

        return render(self.request, self.template_name, {
            "today": today,
            "selected_date": selected_date,
            "is_today": selected_date == today,
            "previous_day": selected_date - timedelta(days=1),
            "next_day": selected_date + timedelta(days=1),
            "can_go_forward": selected_date < today,
            "has_entry": entry is not None,
            "form": form,
            "mood_options": mood_options,
        })