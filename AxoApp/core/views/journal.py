from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View

from ..forms import DiaryEntryForm, GratitudeEntryForm, JournalProfileForm
from ..models import DiaryEntry, GratitudeEntry, JournalProfile


class GratitudeJournalView(LoginRequiredMixin, View):
    template_name = "gratitude_journal.html"
    login_url = "login"

    def get(self, request, *args, **kwargs):
        selected_date = self.get_selected_date(request.GET.get("date"))
        entry = GratitudeEntry.objects.filter(user=request.user, date=selected_date).first()
        form = GratitudeEntryForm(instance=entry)
        return self.render_page(selected_date, entry, form)

    def post(self, request, *args, **kwargs):
        selected_date = self.get_selected_date(request.POST.get("date"))
        entry = GratitudeEntry.objects.filter(user=request.user, date=selected_date).first()
        form = GratitudeEntryForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.date = selected_date
            entry.user = request.user
            entry.save()
            messages.success(request, "Dein Dankbarkeitseintrag wurde gespeichert.")
            return redirect(f"{reverse('gratitude_journal')}?date={selected_date.isoformat()}")
        return self.render_page(selected_date, entry, form)

    def get_selected_date(self, requested_date):
        today = timezone.localdate()
        try:
            selected_date = date.fromisoformat(requested_date) if requested_date else today
        except ValueError:
            selected_date = today
        return min(selected_date, today)

    def render_page(self, selected_date, entry, form):
        today = timezone.localdate()
        return render(self.request, self.template_name, {
            "today": today,
            "selected_date": selected_date,
            "is_today": selected_date == today,
            "previous_day": selected_date - timedelta(days=1),
            "next_day": selected_date + timedelta(days=1),
            "can_go_forward": selected_date < today,
            "entry": entry,
            "form": form,
        })


class JournalProfileView(LoginRequiredMixin, View):
    template_name = "journal_profile.html"
    login_url = "login"

    def get(self, request, *args, **kwargs):
        profile = self.get_profile()
        return render(request, self.template_name, {
            "form": JournalProfileForm(instance=profile),
            "today": timezone.localdate(),
        })

    def post(self, request, *args, **kwargs):
        profile = self.get_profile()
        form = JournalProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Dein Steckbrief wurde gespeichert.")
            return redirect("journal_profile")
        return render(request, self.template_name, {
            "form": form,
            "today": timezone.localdate(),
        })

    def get_profile(self):
        profile, _ = JournalProfile.objects.get_or_create(user=self.request.user)
        return profile


class DiaryEntryView(LoginRequiredMixin, View):
    template_name = "diary_entry.html"
    login_url = "login"

    def get(self, request, *args, **kwargs):
        selected_date = self.get_selected_date(request.GET.get("date"))
        entry = DiaryEntry.objects.filter(user=request.user, date=selected_date).first()
        return self.render_page(selected_date, entry, DiaryEntryForm(instance=entry))

    def post(self, request, *args, **kwargs):
        selected_date = self.get_selected_date(request.POST.get("date"))
        entry = DiaryEntry.objects.filter(user=request.user, date=selected_date).first()
        form = DiaryEntryForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.date = selected_date
            entry.user = request.user
            entry.save()
            messages.success(request, "Dein Tagebucheintrag wurde gespeichert.")
            return redirect(f"{reverse('diary_entry')}?date={selected_date.isoformat()}")
        return self.render_page(selected_date, entry, form)

    def get_selected_date(self, requested_date):
        today = timezone.localdate()
        try:
            selected_date = date.fromisoformat(requested_date) if requested_date else today
        except ValueError:
            selected_date = today
        return min(selected_date, today)

    def render_page(self, selected_date, entry, form):
        today = timezone.localdate()
        return render(self.request, self.template_name, {
            "today": today,
            "selected_date": selected_date,
            "is_today": selected_date == today,
            "previous_day": selected_date - timedelta(days=1),
            "next_day": selected_date + timedelta(days=1),
            "can_go_forward": selected_date < today,
            "entry": entry,
            "form": form,
        })