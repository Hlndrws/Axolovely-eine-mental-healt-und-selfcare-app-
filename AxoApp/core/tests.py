from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import resolve, reverse
from datetime import timedelta

from django.utils import timezone

from .models import (
	DiaryEntry,
	FocusLabel,
	FocusProgress,
	GratitudeEntry,
	HealthDay,
	HydrationDay,
	KitchenTablePerson,
	JournalProfile,
	MoodEntry,
	Routine,
	RoutineCompletion,
)


class MoodTrackerTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username="test-axolovel",
			email="test@example.com",
			password="Valid-test-password-123",
		)
		self.client.force_login(self.user)

	def test_dashboard_shows_calendar_and_tracker_card(self):
		response = self.client.get(reverse("base_page"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Mood Board")
		self.assertContains(response, reverse("mood_tracker"))
		self.assertContains(response, "Axolo-Tea")
		self.assertContains(response, 'btn btn-primary module-cta mt-auto">Auswählen</span>')
		self.assertContains(response, "Gratitude Journal")
		self.assertContains(response, reverse("gratitude_journal"))
		self.assertContains(response, reverse("focus_timer"))
		self.assertContains(response, reverse("journal_profile"))
		self.assertContains(response, "Routinen")
		self.assertContains(response, reverse("kitchen_table"))
		self.assertContains(response, 'class="btn btn-primary module-cta mt-auto', count=5)
		self.assertContains(response, "widget-track")
		self.assertContains(response, "Widgets nach links blättern")
		self.assertContains(response, "Widgets nach rechts blättern")
		for widget in ("Tagebuch", "Hydration", "Healthhub", "Kitchen Table", "Routinen"):
			self.assertContains(response, widget)
		self.assertContains(response, reverse("hydration"))

	def test_burger_menu_only_has_profile_settings_and_themes(self):
		response = self.client.get(reverse("home"))

		self.assertContains(response, 'href="/settings/">Einstellungen</a>')
		self.assertContains(response, 'href="/account/">Profil</a>')
		self.assertContains(response, 'href="/themes/">Axolotl Themes</a>')
		self.assertNotContains(response, 'href="/mood/">Mood Tracker</a>')
		self.assertNotContains(response, 'href="/base/">Dashboard</a>')

	def test_theme_page_is_a_placeholder_for_future_color_modes(self):
		response = self.client.get(reverse("themes"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Axolotl Themes")
		self.assertContains(response, "Farbmodi")

	def test_app_routes_resolve_to_class_based_views(self):
		for route_name in (
			"home", "base_page", "mood_tracker", "account", "app_settings",
			"themes", "axolo_tea", "breathing", "hydration", "focus_timer", "gratitude_journal",
			"journal_profile", "diary_entry", "routines", "health_hub", "kitchen_table", "focus_progress",
			"login", "register", "logout",
		):
			with self.subTest(route=route_name):
				view = resolve(reverse(route_name)).func
				self.assertTrue(
					hasattr(view, "view_class") or route_name in {"login", "logout"}
				)

	def test_profile_offers_login_and_registration_when_signed_out(self):
		self.client.logout()
		response = self.client.get(reverse("account"))

		self.assertContains(response, reverse("login"))
		self.assertContains(response, reverse("register"))

	def test_existing_account_can_log_in(self):
		self.client.logout()
		response = self.client.post(reverse("login"), {
			"username": "test-axolovel",
			"password": "Valid-test-password-123",
		}, follow=True)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.wsgi_request.user.is_authenticated)
		self.assertEqual(response.wsgi_request.user, self.user)

	def test_breathing_page_offers_five_exercises_with_guidance(self):
		response = self.client.get(reverse("breathing"))

		self.assertEqual(response.status_code, 200)
		for exercise in (
			"Lange Ausatmung", "Boxatmung", "Bauchatmung",
			"Gleichmäßiger Atem", "Atem zählen",
		):
			self.assertContains(response, exercise)
		self.assertContains(response, "Wann könnte sie passen?")
		self.assertContains(response, "Übungen nach links blättern")
		self.assertContains(response, "Übungen nach rechts blättern")
		self.assertContains(response, "Übung auswählen")
		self.assertNotContains(response, 'id="breathing-toggle"')

	def test_selected_breathing_exercise_changes_timer_pattern(self):
		response = self.client.get(reverse("breathing"), {"exercise": "box-breathing"})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"label": "Halten", "seconds": 4')
		self.assertContains(response, "breathing-fullscreen")
		self.assertContains(response, 'aria-label="Zurück zur Atemübungs-Auswahl"')
		self.assertContains(response, 'id="breathing-toggle"')

	def test_focus_timer_config_and_zen_garden_are_available(self):
		response = self.client.get(reverse("focus_timer"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Welt aus · Fokus an")
		self.assertContains(response, "Fokuszeit (Minuten)")
		self.assertContains(response, "Pausenzeit (Minuten)")
		self.assertContains(response, "Intervalle pro Runde")
		self.assertContains(response, "Axolotl Zen Garten")
		self.assertContains(response, "1200")
		self.assertContains(response, "Signalton")

	def test_today_entry_is_created_and_updated(self):
		url = reverse("mood_tracker")
		today = timezone.localdate()
		today_url = f"{url}?date={today.isoformat()}"

		response = self.client.post(url, {"mood": "4", "note": "Ein guter Moment"})
		self.assertRedirects(response, today_url)
		self.assertEqual(MoodEntry.objects.count(), 1)

		response = self.client.post(url, {"mood": "5", "note": "Noch besser"})
		self.assertRedirects(response, today_url)
		entry = MoodEntry.objects.get(date=today)
		self.assertEqual(MoodEntry.objects.count(), 1)
		self.assertEqual(entry.mood, 5)
		self.assertEqual(entry.note, "Noch besser")

	def test_mood_entry_saves_selected_and_new_focus_labels(self):
		balance = FocusLabel.objects.get(name="Balance")
		focus = FocusLabel.objects.get(name="Fokus")
		url = reverse("mood_tracker")

		response = self.client.post(url, {
			"mood": "4",
			"note": "Ein guter Moment",
			"focus_labels": [str(balance.id), str(focus.id)],
			"new_focus_label": "Kreativität",
		})

		self.assertRedirects(response, f"{url}?date={timezone.localdate().isoformat()}")
		entry = MoodEntry.objects.get(date=timezone.localdate())
		self.assertSetEqual(
			set(entry.focus_labels.values_list("name", flat=True)),
			{"Balance", "Fokus", "Kreativität"},
		)

		response = self.client.get(reverse("base_page"))
		self.assertContains(response, "Heute lege ich meinen Fokus auf:")
		self.assertContains(response, "Kreativität")

	def test_mood_entry_rejects_more_than_three_focus_labels(self):
		labels = [FocusLabel.objects.create(name=f"Label {index}") for index in range(4)]
		response = self.client.post(reverse("mood_tracker"), {
			"mood": "3",
			"focus_labels": [str(label.id) for label in labels],
		})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(MoodEntry.objects.count(), 0)
		self.assertContains(response, "höchstens drei Fokuslabels")

	def test_default_focus_labels_are_available_in_mood_form(self):
		response = self.client.get(reverse("mood_tracker"))

		for name in ("Balance", "Fokus", "Resilienz", "Innere Ruhe", "Selbstvertrauen", "Zuversicht"):
			self.assertContains(response, name)

	def test_registration_claims_legacy_data_and_logs_new_user_in(self):
		legacy_mood = MoodEntry.objects.create(
			date=timezone.localdate(),
			user=None,
			mood=3,
			note="Legacy-Eintrag",
		)
		self.client.logout()

		response = self.client.post(reverse("register"), {
			"username": "new-person",
			"email": "new@example.com",
			"password1": "Strong-test-password-902!",
			"password2": "Strong-test-password-902!",
		}, follow=True)

		self.assertEqual(response.status_code, 200)
		new_user = get_user_model().objects.get(username="new-person")
		legacy_mood.refresh_from_db()
		self.assertEqual(legacy_mood.user, new_user)
		self.assertEqual(int(response.wsgi_request.user.pk), new_user.pk)

	def test_private_features_redirect_anonymous_visitors_to_login(self):
		self.client.logout()
		for route_name in (
			"base_page", "mood_tracker", "hydration", "health_hub", "focus_timer",
			"gratitude_journal", "journal_profile", "diary_entry", "routines",
		):
			with self.subTest(route=route_name):
				response = self.client.get(reverse(route_name))
				self.assertRedirects(response, f"{reverse('login')}?next={reverse(route_name)}")

	def test_personal_mood_data_is_isolated_between_accounts(self):
		other_user = get_user_model().objects.create_user(
			username="other-person",
			password="Different-test-password-123",
		)
		MoodEntry.objects.create(
			user=other_user,
			date=timezone.localdate(),
			mood=1,
			note="Private fremde Notiz",
		)

		response = self.client.get(reverse("mood_tracker"))

		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, "Private fremde Notiz")
		self.assertFalse(response.context["has_entry"])

	def test_health_hub_saves_daily_steps_and_outdoors_for_current_user(self):
		url = reverse("health_hub")
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

		response = self.client.post(url, {
			"steps": "6400",
			"step_goal": "8000",
			"went_outside": "on",
		})
		self.assertRedirects(response, url)
		health_day = HealthDay.objects.get(user=self.user, date=timezone.localdate())
		self.assertEqual(health_day.steps, 6400)
		self.assertEqual(health_day.step_goal, 8000)
		self.assertTrue(health_day.went_outside)

	def test_kitchen_table_people_can_be_added_edited_and_removed_privately(self):
		url = reverse("kitchen_table")
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Wer gibt dir das Gefühl")

		response = self.client.post(url, {
			"action": "save",
			"name": "Mira",
			"appreciation": "Sie hört mir aufmerksam zu.",
			"care_idea": "Wir trinken am Wochenende zusammen Tee.",
		})
		self.assertRedirects(response, url)
		person = KitchenTablePerson.objects.get(user=self.user, name="Mira")

		response = self.client.post(url, {
			"action": "save",
			"person_id": str(person.pk),
			"name": "Mira",
			"appreciation": "Sie bringt mich oft zum Lachen.",
			"care_idea": "Zusammen spazieren gehen.",
		})
		self.assertRedirects(response, url)
		person.refresh_from_db()
		self.assertEqual(person.appreciation, "Sie bringt mich oft zum Lachen.")

		other_user = get_user_model().objects.create_user(
			username="kitchen-table-other",
			password="Different-kitchen-password-789",
		)
		self.client.force_login(other_user)
		self.assertNotContains(self.client.get(url), "Mira")
		response = self.client.post(url, {"action": "delete", "person_id": str(person.pk)})
		self.assertEqual(response.status_code, 404)
		self.assertTrue(KitchenTablePerson.objects.filter(pk=person.pk).exists())

		self.client.force_login(self.user)
		response = self.client.post(url, {"action": "delete", "person_id": str(person.pk)})
		self.assertRedirects(response, url)
		self.assertFalse(KitchenTablePerson.objects.filter(pk=person.pk).exists())

	def test_focus_progress_is_saved_to_the_current_account(self):
		response = self.client.post(reverse("focus_progress"), {"seconds": "42"})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["focused_seconds"], 42)
		self.assertEqual(FocusProgress.objects.get(user=self.user).focused_seconds, 42)

		other_user = get_user_model().objects.create_user(
			username="focus-neighbor",
			password="Different-test-password-456",
		)
		self.assertFalse(FocusProgress.objects.filter(user=other_user).exists())

	def test_hydration_starts_with_two_liter_goal_and_adds_250_ml_per_glass(self):
		url = reverse("hydration")
		response = self.client.get(url)

		self.assertEqual(response.status_code, 200)
		hydration_day = HydrationDay.objects.get(date=timezone.localdate())
		self.assertEqual(hydration_day.goal_ml, 2000)
		self.assertEqual(hydration_day.consumed_ml, 0)
		self.assertContains(response, "2–3 Liter")
		self.assertNotContains(response, "rückgängig")

		for glass_number, expected_amount in ((1, 250), (2, 500)):
			response = self.client.post(url, {
				"action": "toggle_glass",
				"glass_number": str(glass_number),
			})
			self.assertRedirects(response, url)
			hydration_day.refresh_from_db()
			self.assertEqual(hydration_day.consumed_ml, expected_amount)

	def test_hydration_last_filled_glass_can_be_undone(self):
		url = reverse("hydration")
		self.client.get(url)
		self.client.post(url, {"action": "toggle_glass", "glass_number": "1"})
		self.client.post(url, {"action": "toggle_glass", "glass_number": "2"})
		hydration_day = HydrationDay.objects.get(date=timezone.localdate())
		self.assertEqual(hydration_day.consumed_ml, 500)

		response = self.client.post(url, {"action": "toggle_glass", "glass_number": "1"})
		self.assertRedirects(response, url)
		hydration_day.refresh_from_db()
		self.assertEqual(hydration_day.consumed_ml, 500)

		response = self.client.post(url, {"action": "toggle_glass", "glass_number": "2"})
		self.assertRedirects(response, url)
		hydration_day.refresh_from_db()
		self.assertEqual(hydration_day.consumed_ml, 250)

	def test_hydration_goal_can_be_changed_and_invalid_goal_is_rejected(self):
		url = reverse("hydration")
		self.client.get(url)

		response = self.client.post(url, {"action": "save_goal", "goal_liters": "2.5"})
		self.assertRedirects(response, url)
		hydration_day = HydrationDay.objects.get(date=timezone.localdate())
		self.assertEqual(hydration_day.goal_ml, 2500)

		response = self.client.post(url, {"action": "save_goal", "goal_liters": "8"})
		self.assertEqual(response.status_code, 200)
		hydration_day.refresh_from_db()
		self.assertEqual(hydration_day.goal_ml, 2500)
		self.assertContains(response, "Ensure this value is less than or equal to 5")

	def test_gratitude_journal_saves_entry_for_selected_date(self):
		url = reverse("gratitude_journal")
		today = timezone.localdate()

		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Heute bin ich dankbar für")
		self.assertContains(response, today.strftime("%d.%m.%Y"))
		self.assertContains(response, "journal-writing")

		response = self.client.post(url, {
			"date": today.isoformat(),
			"text": "Für einen schönen Spaziergang und einen lieben Anruf.",
		})
		self.assertRedirects(response, f"{url}?date={today.isoformat()}")
		entry = GratitudeEntry.objects.get(date=today)
		self.assertEqual(entry.text, "Für einen schönen Spaziergang und einen lieben Anruf.")

		response = self.client.get(url, {"date": today.isoformat()})
		self.assertContains(response, entry.text)

	def test_journal_profile_saves_all_personal_prompts(self):
		url = reverse("journal_profile")
		response = self.client.get(url)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Mein Steckbrief")
		self.assertContains(response, "Weiterblättern zum Tagebuch")
		for prompt in (
			"Name", "Spitzname", "Hobbys", "Mein perfekter freier Tag", "Lieblingstee",
			"Lieblingsband", "Lieblingsfilm", "Traumziel", "Das möchte ich noch lernen",
			"Darin bin ich schon super", "Das mag ich an mir",
		):
			self.assertContains(response, prompt)

		response = self.client.post(url, {
			"name": "Alex",
			"nickname": "Axi",
			"hobbies": "Lesen und malen",
			"perfect_free_day": "Tee trinken und am See spazieren",
			"favorite_tea": "Jasmin",
			"favorite_band": "Lieblingsband",
			"favorite_film": "Lieblingsfilm",
			"dream_destination": "Japan",
			"want_to_learn": "Klavier spielen",
			"good_at": "Gut zuhören",
			"like_about_myself": "Meine Geduld",
		})
		self.assertRedirects(response, url)
		profile = JournalProfile.objects.get(user=self.user)
		self.assertEqual(profile.name, "Alex")
		self.assertEqual(profile.favorite_tea, "Jasmin")
		self.assertEqual(profile.like_about_myself, "Meine Geduld")

		response = self.client.post(url, {"name": "Sam"}, follow=True)
		self.assertContains(response, "data-dismiss-message")
		self.assertContains(response, "message-close")

	def test_diary_pages_save_and_reopen_by_date(self):
		url = reverse("diary_entry")
		entry_date = timezone.localdate() - timedelta(days=1)

		response = self.client.get(url, {"date": entry_date.isoformat()})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Tagebuch · ab Seite 2")

		response = self.client.post(url, {
			"date": entry_date.isoformat(),
			"text": "Heute habe ich etwas Neues gelernt.",
		})
		self.assertRedirects(response, f"{url}?date={entry_date.isoformat()}")
		entry = DiaryEntry.objects.get(date=entry_date)
		self.assertEqual(entry.text, "Heute habe ich etwas Neues gelernt.")

		response = self.client.get(url, {"date": entry_date.isoformat()})
		self.assertContains(response, entry.text)

	def test_invalid_mood_is_not_saved(self):
		response = self.client.post(reverse("mood_tracker"), {"mood": "8", "note": "Ungültig"})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(MoodEntry.objects.count(), 0)

	def test_calendar_shows_saved_mood_for_day(self):
		today = timezone.localdate()
		MoodEntry.objects.create(date=today, user=self.user, mood=3, note="Ganz okay")

		response = self.client.get(reverse("base_page"))

		self.assertContains(response, "Neutral")
		self.assertContains(response, 'alt="Neutral"')

	def test_dashboard_shows_top_three_mood_percentages(self):
		today = timezone.localdate()
		day_offset = 0
		for mood, count in ((5, 4), (4, 3), (3, 2), (2, 1)):
			for _ in range(count):
				MoodEntry.objects.create(
					date=today - timedelta(days=day_offset),
					user=self.user,
					mood=mood,
					note="",
				)
				day_offset += 1

		response = self.client.get(reverse("base_page"))

		self.assertContains(response, "Top-Stimmungen")
		self.assertContains(response, "40%")
		self.assertContains(response, "30%")
		self.assertContains(response, "20%")

	def test_past_entry_can_be_opened_and_updated(self):
		past_date = timezone.localdate() - timedelta(days=1)
		MoodEntry.objects.create(date=past_date, user=self.user, mood=1, note="Ein schwieriger Tag")
		url = reverse("mood_tracker")

		response = self.client.get(url, {"date": past_date.isoformat()})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Ein schwieriger Tag")
		self.assertContains(response, past_date.strftime("%d.%m.%Y"))
		self.assertEqual(response.context["form"]["mood"].value(), 1)

		response = self.client.post(url, {
			"date": past_date.isoformat(),
			"mood": "2",
			"note": "Der Tag war doch etwas besser",
		})
		self.assertRedirects(response, f"{url}?date={past_date.isoformat()}")
		entry = MoodEntry.objects.get(date=past_date)
		self.assertEqual(entry.mood, 2)
		self.assertEqual(entry.note, "Der Tag war doch etwas besser")

	def test_shared_layout_uses_heart_as_favicon(self):
		response = self.client.get(reverse("home"))

		self.assertContains(response, '/static/pics/heart.png')

	def test_axolo_tea_offers_tea_time_and_breathing(self):
		response = self.client.get(reverse("axolo_tea"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Tea Time")
		self.assertContains(response, "Durchatmen")
		self.assertContains(response, reverse("breathing"))
		self.assertContains(response, "back-arrow")

	def test_breathing_page_has_start_and_pause_control(self):
		response = self.client.get(reverse("breathing"), {"exercise": "long-exhale"})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Einatmen")
		self.assertContains(response, 'id="breathing-toggle"')

	def test_routines_can_be_added_completed_and_removed(self):
		url = reverse("routines")
		response = self.client.post(url, {"action": "add", "title": "Zähne putzen"})
		self.assertRedirects(response, url)
		routine = Routine.objects.get(title="Zähne putzen")

		response = self.client.post(url, {"action": "toggle", "routine_id": routine.id})
		self.assertRedirects(response, url)
		self.assertTrue(RoutineCompletion.objects.filter(routine=routine, date=timezone.localdate()).exists())

		response = self.client.post(url, {"action": "toggle", "routine_id": routine.id})
		self.assertRedirects(response, url)
		self.assertFalse(RoutineCompletion.objects.filter(routine=routine, date=timezone.localdate()).exists())

		response = self.client.post(url, {"action": "delete", "routine_id": routine.id})
		self.assertRedirects(response, url)
		self.assertFalse(Routine.objects.filter(pk=routine.id).exists())

	def test_routine_completion_is_scoped_to_day(self):
		routine = Routine.objects.create(title="Spazieren gehen", user=self.user)
		yesterday = timezone.localdate() - timedelta(days=1)
		RoutineCompletion.objects.create(routine=routine, date=yesterday)

		response = self.client.get(reverse("routines"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["daily_completed_count"], 0)
		self.assertContains(response, "Spazieren gehen")
		self.assertContains(response, "Einmal pro Woche")
		self.assertContains(response, "routine-remove")

	def test_weekly_routine_can_be_completed_once_per_week(self):
		routine = Routine.objects.create(title="Lange spazieren gehen", frequency="weekly", user=self.user)
		url = reverse("routines")
		today = timezone.localdate()
		week_start = today - timedelta(days=today.weekday())
		previous_day_this_week = today - timedelta(days=1) if today.weekday() else today
		if previous_day_this_week == today:
			completed_date = today
		else:
			completed_date = previous_day_this_week
		RoutineCompletion.objects.create(routine=routine, date=completed_date)

		response = self.client.get(url)
		self.assertEqual(response.context["weekly_completed_count"], 1)
		self.assertContains(response, "Lange spazieren gehen")

		response = self.client.post(url, {"action": "toggle", "routine_id": routine.id})
		self.assertRedirects(response, url)
		self.assertFalse(RoutineCompletion.objects.filter(
			routine=routine,
			date__range=(week_start, week_start + timedelta(days=6)),
		).exists())

		response = self.client.post(url, {"action": "toggle", "routine_id": routine.id})
		self.assertRedirects(response, url)
		self.assertTrue(RoutineCompletion.objects.filter(routine=routine, date=today).exists())
