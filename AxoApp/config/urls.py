"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from core.views import (
    AccountView,
    AppSettingsView,
    AxoloTeaView,
    AxolotlThemesView,
    BreathingView,
    DashboardView,
    DiaryEntryView,
    FocusTimerView,
    FocusProgressView,
    HealthHubView,
    GratitudeJournalView,
    HomeView,
    HydrationView,
    JournalProfileView,
    KitchenTableView,
    MoodTrackerView,
    RoutinesView,
    RegistrationView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"), #Startseite am Anfang
    path("base/", DashboardView.as_view(), name="base_page"), #dashboard
    path("mood/", MoodTrackerView.as_view(), name="mood_tracker"),
    path("account/", AccountView.as_view(), name="account"),
    path("account/login/", LoginView.as_view(
        template_name="registration/login.html",
        redirect_authenticated_user=True,
    ), name="login"),
    path("account/register/", RegistrationView.as_view(), name="register"),
    path("account/logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("settings/", AppSettingsView.as_view(), name="app_settings"),
    path("themes/", AxolotlThemesView.as_view(), name="themes"),
    path("tea/", AxoloTeaView.as_view(), name="axolo_tea"),
    path("tea/breathe/", BreathingView.as_view(), name="breathing"),
    path("focus/", FocusTimerView.as_view(), name="focus_timer"),
    path("focus/progress/", FocusProgressView.as_view(), name="focus_progress"),
    path("health/", HealthHubView.as_view(), name="health_hub"),
    path("hydration/", HydrationView.as_view(), name="hydration"),
    path("gratitude/", GratitudeJournalView.as_view(), name="gratitude_journal"),
    path("journal/", JournalProfileView.as_view(), name="journal_profile"),
    path("journal/entry/", DiaryEntryView.as_view(), name="diary_entry"),
    path("kitchen-table/", KitchenTableView.as_view(), name="kitchen_table"),
    path("routines/", RoutinesView.as_view(), name="routines"),
]