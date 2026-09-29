from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from ..models import FocusProgress


class FocusTimerView(LoginRequiredMixin, TemplateView):
    template_name = "focus_timer.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        progress, _ = FocusProgress.objects.get_or_create(user=self.request.user)
        context["focused_seconds"] = progress.focused_seconds
        return context


class FocusProgressView(LoginRequiredMixin, View):
    login_url = "login"

    def post(self, request, *args, **kwargs):
        try:
            seconds = int(request.POST.get("seconds", ""))
        except (TypeError, ValueError):
            return JsonResponse({"error": "Ungültige Fokuszeit."}, status=400)
        if not 1 <= seconds <= 60:
            return JsonResponse({"error": "Fokuszeit muss zwischen 1 und 60 Sekunden liegen."}, status=400)

        progress, _ = FocusProgress.objects.get_or_create(user=request.user)
        FocusProgress.objects.filter(pk=progress.pk).update(
            focused_seconds=F("focused_seconds") + seconds,
            updated_at=timezone.now(),
        )
        progress.refresh_from_db()
        return JsonResponse({"focused_seconds": progress.focused_seconds})
