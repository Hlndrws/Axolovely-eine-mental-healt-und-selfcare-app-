from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import (
    DiaryEntry,
    FocusLabel,
    GratitudeEntry,
    HealthDay,
    JournalProfile,
    KitchenTablePerson,
    MoodEntry,
    Routine,
)

User = get_user_model()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "autocomplete": "username"})
        self.fields["password1"].widget.attrs.update({"class": "form-control", "autocomplete": "new-password"})
        self.fields["password2"].widget.attrs.update({"class": "form-control", "autocomplete": "new-password"})

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Für diese E-Mail-Adresse gibt es bereits ein Konto.")
        return email


class HealthDayForm(forms.ModelForm):
    class Meta:
        model = HealthDay
        fields = ["steps", "step_goal", "went_outside"]
        labels = {
            "steps": "Schritte heute",
            "step_goal": "Schrittziel",
            "went_outside": "Heute draußen gewesen",
        }


class KitchenTablePersonForm(forms.ModelForm):
    class Meta:
        model = KitchenTablePerson
        fields = ["name", "avatar_gender", "avatar_hair_color", "avatar_glasses", "appreciation", "care_idea"]
        labels = {
            "name": "Name oder Spitzname",
            "avatar_gender": "Figur",
            "avatar_hair_color": "Haarfarbe",
            "avatar_glasses": "Brille",
            "appreciation": "Was schätze ich an dieser Person?",
            "care_idea": "Wie möchte ich diese Freundschaft pflegen?",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "maxlength": 100}),
            "avatar_gender": forms.RadioSelect(attrs={"class": "avatar-gender-radio"}),
            "avatar_hair_color": forms.RadioSelect(attrs={"class": "avatar-color-radio"}),
            "avatar_glasses": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "appreciation": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "care_idea": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class MoodEntryForm(forms.Form):
    mood = forms.ChoiceField(choices=MoodEntry.MOOD_CHOICES)
    note = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 4, "maxlength": 500}),
    )
    focus_labels = forms.ModelMultipleChoiceField(
        queryset=FocusLabel.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    new_focus_label = forms.CharField(required=False, max_length=40)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["focus_labels"].queryset = FocusLabel.objects.filter(
            Q(user__isnull=True) | Q(user=user)
        )

    def clean(self):
        cleaned_data = super().clean()
        selected_labels = cleaned_data.get("focus_labels", [])
        new_label = (cleaned_data.get("new_focus_label") or "").strip()
        already_selected = any(
            label.name.casefold() == new_label.casefold()
            for label in selected_labels
        )
        if len(selected_labels) + bool(new_label and not already_selected) > 3:
            raise ValidationError("Du kannst höchstens drei Fokuslabels auswählen.")
        cleaned_data["new_focus_label"] = new_label
        return cleaned_data


class HydrationGoalForm(forms.Form):
    goal_liters = forms.DecimalField(
        min_value=0.5,
        max_value=5,
        max_digits=3,
        decimal_places=2,
        initial=2,
        label="Dein Tagesziel in Litern",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "min": "0.5",
            "max": "5",
            "step": "0.25",
        }),
    )


class GratitudeEntryForm(forms.ModelForm):
    class Meta:
        model = GratitudeEntry
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={
                "class": "form-control journal-writing",
                "rows": 12,
                "maxlength": 10000,
                "placeholder": "Nimm dir einen Moment und schreib auf, was dir heute wichtig ist ...",
            }),
        }


class JournalProfileForm(forms.ModelForm):
    class Meta:
        model = JournalProfile
        fields = [
            "name", "nickname", "hobbies", "perfect_free_day", "favorite_tea",
            "favorite_band", "favorite_film", "dream_destination", "want_to_learn",
            "good_at", "like_about_myself",
        ]
        labels = {
            "name": "Name",
            "nickname": "Spitzname",
            "hobbies": "Hobbys",
            "perfect_free_day": "Mein perfekter freier Tag",
            "favorite_tea": "Lieblingstee",
            "favorite_band": "Lieblingsband",
            "favorite_film": "Lieblingsfilm",
            "dream_destination": "Traumziel",
            "want_to_learn": "Das möchte ich noch lernen",
            "good_at": "Darin bin ich schon super",
            "like_about_myself": "Das mag ich an mir",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "nickname": forms.TextInput(attrs={"class": "form-control"}),
            "hobbies": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "perfect_free_day": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "favorite_tea": forms.TextInput(attrs={"class": "form-control"}),
            "favorite_band": forms.TextInput(attrs={"class": "form-control"}),
            "favorite_film": forms.TextInput(attrs={"class": "form-control"}),
            "dream_destination": forms.TextInput(attrs={"class": "form-control"}),
            "want_to_learn": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "good_at": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "like_about_myself": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class DiaryEntryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={
                "class": "form-control diary-writing",
                "rows": 12,
                "maxlength": 10000,
                "placeholder": "Was möchtest du von deinem Tag festhalten?",
            }),
        }


class RoutineForm(forms.ModelForm):
    frequency = forms.ChoiceField(
        choices=Routine.FREQUENCY_CHOICES,
        initial="daily",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Routine
        fields = ["title", "frequency"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "maxlength": 100,
                "placeholder": "Zum Beispiel: draußen spazieren gehen",
            }),
        }

    def clean_frequency(self):
        return self.cleaned_data.get("frequency") or "daily"