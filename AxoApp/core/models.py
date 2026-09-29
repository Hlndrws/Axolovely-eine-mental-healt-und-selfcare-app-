from django.conf import settings
from django.db import models
from django.utils import timezone


class FocusLabel(models.Model):
	name = models.CharField(max_length=40)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		related_name="focus_labels",
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["name"]
		constraints = [
			models.UniqueConstraint(fields=["user", "name"], name="unique_focus_label_per_user"),
		]

	def __str__(self):
		return self.name


class MoodEntry(models.Model):
	MOOD_CHOICES = [
		(1, "Sehr schlecht"),
		(2, "Eher schlecht"),
		(3, "Neutral"),
		(4, "Eher gut"),
		(5, "Super"),
	]

	date = models.DateField(default=timezone.localdate)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
		related_name="mood_entries",
	)
	mood = models.PositiveSmallIntegerField(choices=MOOD_CHOICES)
	note = models.TextField(blank=True)
	focus_labels = models.ManyToManyField("FocusLabel", blank=True, related_name="mood_entries")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date"]
		constraints = [
			models.UniqueConstraint(fields=["user", "date"], name="unique_mood_entry_per_user_day"),
		]

	def __str__(self):
		return f"{self.date}: {self.get_mood_display()}"


class HydrationDay(models.Model):
	date = models.DateField(default=timezone.localdate)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
		related_name="hydration_days",
	)
	goal_ml = models.PositiveIntegerField(default=2000)
	consumed_ml = models.PositiveIntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date"]
		constraints = [
			models.UniqueConstraint(fields=["user", "date"], name="unique_hydration_day_per_user"),
		]

	def __str__(self):
		return f"{self.date}: {self.consumed_ml} / {self.goal_ml} ml"


class HealthDay(models.Model):
	date = models.DateField(default=timezone.localdate)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
		related_name="health_days",
	)
	steps = models.PositiveIntegerField(default=0)
	step_goal = models.PositiveIntegerField(default=8000)
	went_outside = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date"]
		constraints = [
			models.UniqueConstraint(fields=["user", "date"], name="unique_health_day_per_user"),
		]

	def __str__(self):
		return f"{self.date}: {self.steps} / {self.step_goal} Schritte"


class FocusProgress(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="focus_progress")
	focused_seconds = models.PositiveBigIntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.user}: {self.focused_seconds} Fokus-Sekunden"


class KitchenTablePerson(models.Model):
	AVATAR_CHOICES = [
		("😊", "😊"), ("🌸", "🌸"), ("🦋", "🦋"), ("🌼", "🌼"),
		("🍵", "🍵"), ("🌙", "🌙"), ("⭐", "⭐"), ("💗", "💗"),
		("🍀", "🍀"), ("🐰", "🐰"), ("🦊", "🦊"), ("🐢", "🐢"),
		("🐼", "🐼"), ("🐙", "🐙"), ("🦥", "🦥"), ("🌻", "🌻"),
	]

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="kitchen_table_people")
	name = models.CharField(max_length=100)
	avatar = models.CharField(max_length=8, choices=AVATAR_CHOICES, default="😊")
	appreciation = models.TextField(blank=True)
	care_idea = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["name", "id"]

	def __str__(self):
		return self.name


class GratitudeEntry(models.Model):
	date = models.DateField(default=timezone.localdate)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
		related_name="gratitude_entries",
	)
	text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date"]
		constraints = [
			models.UniqueConstraint(fields=["user", "date"], name="unique_gratitude_entry_per_user_day"),
		]

	def __str__(self):
		return f"Dankbarkeit am {self.date}"


class JournalProfile(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
		related_name="journal_profile",
	)
	name = models.CharField(max_length=100, blank=True)
	nickname = models.CharField(max_length=100, blank=True)
	hobbies = models.TextField(blank=True)
	perfect_free_day = models.TextField(blank=True)
	favorite_tea = models.CharField(max_length=100, blank=True)
	favorite_band = models.CharField(max_length=100, blank=True)
	favorite_film = models.CharField(max_length=100, blank=True)
	dream_destination = models.CharField(max_length=100, blank=True)
	want_to_learn = models.TextField(blank=True)
	good_at = models.TextField(blank=True)
	like_about_myself = models.TextField(blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name or "Mein Tagebuch-Steckbrief"


class DiaryEntry(models.Model):
	date = models.DateField(default=timezone.localdate)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
		related_name="diary_entries",
	)
	text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date"]
		constraints = [
			models.UniqueConstraint(fields=["user", "date"], name="unique_diary_entry_per_user_day"),
		]

	def __str__(self):
		return f"Tagebucheintrag am {self.date}"


class Routine(models.Model):
	FREQUENCY_CHOICES = [
		("daily", "Täglich"),
		("weekly", "Einmal pro Woche"),
	]

	title = models.CharField(max_length=100)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
		related_name="routines",
	)
	frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="daily")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["created_at", "id"]

	def __str__(self):
		return self.title


class RoutineCompletion(models.Model):
	routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name="completions")
	date = models.DateField(default=timezone.localdate)
	completed_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["routine", "date"], name="unique_routine_completion_per_day"),
		]
