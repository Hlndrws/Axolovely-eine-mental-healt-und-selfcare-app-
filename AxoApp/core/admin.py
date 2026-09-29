from django.contrib import admin

from .models import (
	DiaryEntry,
	FocusLabel,
	FocusProgress,
	GratitudeEntry,
	HealthDay,
	HydrationDay,
	JournalProfile,
	KitchenTablePerson,
	MoodEntry,
	Routine,
	RoutineCompletion,
)


admin.site.register(MoodEntry)
admin.site.register(FocusLabel)
admin.site.register(HydrationDay)
admin.site.register(HealthDay)
admin.site.register(FocusProgress)
admin.site.register(GratitudeEntry)
admin.site.register(JournalProfile)
admin.site.register(KitchenTablePerson)
admin.site.register(DiaryEntry)
admin.site.register(Routine)
admin.site.register(RoutineCompletion)
