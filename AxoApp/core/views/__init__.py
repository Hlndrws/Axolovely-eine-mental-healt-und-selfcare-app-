from .dashboard import DashboardView
from .auth import HealthHubView, RegistrationView
from .focus import FocusProgressView, FocusTimerView
from .hydration import HydrationView
from .journal import DiaryEntryView, GratitudeJournalView, JournalProfileView
from .mood import MoodTrackerView
from .pages import (
    AccountView,
    AppSettingsView,
    AxoloTeaView,
    AxolotlThemesView,
    BreathingView,
    HomeView,
)
from .routines import RoutinesView

__all__ = [
    "AccountView",
    "AppSettingsView",
    "AxoloTeaView",
    "AxolotlThemesView",
    "BreathingView",
    "DashboardView",
    "DiaryEntryView",
    "FocusTimerView",
    "FocusProgressView",
    "GratitudeJournalView",
    "HomeView",
    "HealthHubView",
    "HydrationView",
    "JournalProfileView",
    "MoodTrackerView",
    "RoutinesView",
    "RegistrationView",
]