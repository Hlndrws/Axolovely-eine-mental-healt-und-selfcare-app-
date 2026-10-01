from django.contrib import admin

#Verwaltungsoberfläche

from .models import (   #Hier werden die Models importiert (DBs)
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

#In admin.py legst du fest, welche deiner Datenbank-Modelle im Django-Admin-Bereich 
# sichtbar und verwaltbar sind.
