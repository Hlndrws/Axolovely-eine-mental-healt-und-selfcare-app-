from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView

from ..forms import HealthDayForm, RegistrationForm
from ..models import (
	DiaryEntry,
	FocusLabel,
	GratitudeEntry,
	HydrationDay,
	HealthDay,
	JournalProfile,
	MoodEntry,
	Routine,
)


class RegistrationView(FormView):
	template_name = "registration/register.html"
	form_class = RegistrationForm
	success_url = reverse_lazy("base_page")

	def form_valid(self, form):
		user = form.save()
		self.claim_legacy_data(user)
		login(self.request, user)
		messages.success(self.request, "Dein Axolovel-Konto ist bereit.")
		return redirect(self.get_success_url())

	@transaction.atomic
	def claim_legacy_data(self, user):
		for model in (MoodEntry, HydrationDay, GratitudeEntry, DiaryEntry, Routine):
			model.objects.filter(user__isnull=True).update(user=user)

		profile = JournalProfile.objects.filter(user__isnull=True).first()
		if profile:
			profile.user = user
			profile.save(update_fields=["user"])

		default_labels = ("Balance", "Fokus", "Resilienz", "Innere Ruhe", "Selbstvertrauen", "Zuversicht")
		FocusLabel.objects.filter(user__isnull=True).exclude(name__in=default_labels).update(user=user)


class HealthHubView(LoginRequiredMixin, FormView):
	template_name = "health_hub.html"
	form_class = HealthDayForm
	login_url = reverse_lazy("login")

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["instance"] = self.get_today_record()
		return kwargs

	def get_today_record(self):
		day, _ = HealthDay.objects.get_or_create(user=self.request.user, date=timezone.localdate())
		return day

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		health_day = self.get_today_record()
		context["health_day"] = health_day
		context["step_progress"] = min(100, round(health_day.steps * 100 / health_day.step_goal))
		context["steps_remaining"] = max(0, health_day.step_goal - health_day.steps)
		return context

	def form_valid(self, form):
		health_day = form.save(commit=False)
		health_day.user = self.request.user
		health_day.date = self.get_today_record().date
		health_day.save()
		messages.success(self.request, "Dein heutiger Health-Hub-Stand wurde gespeichert.")
		return redirect("health_hub")