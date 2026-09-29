import calendar
from datetime import date, datetime

from django.contrib.staticfiles import finders
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.templatetags.static import static
from django.utils import timezone
from django.views.generic import TemplateView

from ..models import MoodEntry
from .constants import MONTH_NAMES, MOOD_FACES


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"
    login_url = "login"
    weekdays = ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        selected_month = self.get_selected_month(today)
        year, month = selected_month.year, selected_month.month
        previous_month = date(year - (month == 1), 12 if month == 1 else month - 1, 1)
        next_month = date(year + (month == 12), 1 if month == 12 else month + 1, 1)

        context.update({
            "today": today,
            "today_focus_labels": self.get_today_focus_labels(today),
            "month_title": f"{MONTH_NAMES[month - 1]} {year}",
            "previous_month": previous_month.strftime("%Y-%m"),
            "next_month": next_month.strftime("%Y-%m"),
            "weekdays": self.weekdays,
            "weeks": self.build_calendar(year, month, today),
            "top_moods": self.get_top_moods(),
        })
        return context

    def get_today_focus_labels(self, today):
        entry = MoodEntry.objects.filter(user=self.request.user, date=today).first()
        return entry.focus_labels.all() if entry else []

    def get_selected_month(self, today):
        try:
            requested_month = datetime.strptime(self.request.GET.get("month", ""), "%Y-%m")
            return requested_month.date().replace(day=1)
        except ValueError:
            return today.replace(day=1)

    def build_calendar(self, year, month, today):
        entries_by_date = {
            entry.date: entry
            for entry in MoodEntry.objects.filter(
                user=self.request.user,
                date__year=year,
                date__month=month,
            )
        }
        weeks = []
        for week in calendar.Calendar(firstweekday=0).monthdayscalendar(year, month):
            calendar_week = []
            for day in week:
                if day == 0:
                    calendar_week.append({"empty": True})
                    continue

                current_date = date(year, month, day)
                entry = entries_by_date.get(current_date)
                mood_image = f"pics/mood{entry.mood}.png" if entry else ""
                calendar_week.append({
                    "day": day,
                    "date": current_date,
                    "date_value": current_date.isoformat(),
                    "is_future": current_date > today,
                    "is_today": current_date == today,
                    "entry": entry,
                    "mood_image_url": static(mood_image) if entry else "",
                    "has_mood_image": bool(finders.find(mood_image)) if entry else False,
                    "mood_face": MOOD_FACES.get(entry.mood, "") if entry else "",
                })
            weeks.append(calendar_week)
        return weeks

    def get_top_moods(self):
        user_entries = MoodEntry.objects.filter(user=self.request.user)
        total_entries = user_entries.count()
        if not total_entries:
            return []

        mood_labels = dict(MoodEntry.MOOD_CHOICES)
        most_frequent = (
            user_entries.values("mood")
            .annotate(entry_count=Count("id"))
            .order_by("-entry_count", "mood")[:3]
        )
        return [
            {
                "label": mood_labels[item["mood"]],
                "percentage": round(item["entry_count"] * 100 / total_entries),
                "entry_count": item["entry_count"],
                "image_url": static(f"pics/mood{item['mood']}.png"),
                "has_image": bool(finders.find(f"pics/mood{item['mood']}.png")),
                "face": MOOD_FACES[item["mood"]],
            }
            for item in most_frequent
        ]