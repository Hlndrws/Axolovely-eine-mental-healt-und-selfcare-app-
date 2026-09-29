from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "home.html"


class AccountView(TemplateView):
    template_name = "account.html"


class AppSettingsView(TemplateView):
    template_name = "settings.html"


class AxolotlThemesView(TemplateView):
    template_name = "themes.html"


class AxoloTeaView(TemplateView):
    template_name = "axolo_tea.html"
    tea_signs = [
        "Du musst nicht alles heute schaffen.",
        "Eine Pause ist auch ein produktiver Schritt.",
        "Du darfst stolz auf kleine Fortschritte sein.",
        "Atme aus. Du bist genau hier.",
        "Sei heute so freundlich zu dir wie zu einem guten Freund.",
        "Langsam ist auch ein Tempo.",
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tea_signs"] = self.tea_signs
        return context


class BreathingView(TemplateView):
    template_name = "breathing.html"
    exercises = [
        {
            "id": "long-exhale",
            "name": "Lange Ausatmung",
            "summary": "4 Sekunden ein, 6 Sekunden aus.",
            "for_when": "Wenn du eine ruhige, einfache Pause möchtest oder dich gerade angespannt fühlst.",
            "steps": [
                {"label": "Einatmen", "seconds": 4},
                {"label": "Ausatmen", "seconds": 6},
            ],
        },
        {
            "id": "box-breathing",
            "name": "Boxatmung",
            "summary": "Vier gleich lange Phasen mit je 4 Sekunden.",
            "for_when": "Wenn du einen klaren, gleichmäßigen Rhythmus magst. Die Atempausen kannst du auslassen, wenn sie unangenehm sind.",
            "steps": [
                {"label": "Einatmen", "seconds": 4},
                {"label": "Halten", "seconds": 4},
                {"label": "Ausatmen", "seconds": 4},
                {"label": "Halten", "seconds": 4},
            ],
        },
        {
            "id": "belly-breathing",
            "name": "Bauchatmung",
            "summary": "Sanft in den Bauch einatmen und langsam ausatmen.",
            "for_when": "Wenn du deine Aufmerksamkeit auf eine weiche, natürliche Atmung lenken möchtest.",
            "steps": [
                {"label": "Sanft einatmen", "seconds": 4},
                {"label": "Langsam ausatmen", "seconds": 6},
            ],
        },
        {
            "id": "even-breathing",
            "name": "Gleichmäßiger Atem",
            "summary": "5 Sekunden ein, 5 Sekunden aus.",
            "for_when": "Wenn du einen ausgeglichenen Takt ohne Atempausen ausprobieren möchtest.",
            "steps": [
                {"label": "Einatmen", "seconds": 5},
                {"label": "Ausatmen", "seconds": 5},
            ],
        },
        {
            "id": "counting-breath",
            "name": "Atem zählen",
            "summary": "Atme bequem ein und zähle beim Ausatmen langsam bis 5.",
            "for_when": "Wenn deine Gedanken wandern und du ihnen einen sanften Anker geben möchtest.",
            "steps": [
                {"label": "Einatmen", "seconds": 4},
                {"label": "Ausatmen und bis 5 zählen", "seconds": 6},
            ],
        },
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise_id = self.request.GET.get("exercise")
        selected_exercise = (
            next((exercise for exercise in self.exercises if exercise["id"] == exercise_id), None)
            if exercise_id
            else None
        )
        context.update({
            "exercises": self.exercises,
            "selected_exercise": selected_exercise,
            "is_fullscreen": selected_exercise is not None,
        })
        return context