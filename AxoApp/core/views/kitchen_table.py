from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from ..forms import KitchenTablePersonForm
from ..models import KitchenTablePerson


class KitchenTableView(LoginRequiredMixin, View):
	login_url = "login"
	template_name = "kitchen_table.html"

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {
			"people": KitchenTablePerson.objects.filter(user=request.user),
			"form": KitchenTablePersonForm(),
		})

	def post(self, request, *args, **kwargs):
		action = request.POST.get("action", "add")
		if action == "delete":
			person = get_object_or_404(
				KitchenTablePerson,
				pk=request.POST.get("person_id"),
				user=request.user,
			)
			person.delete()
			messages.success(request, "Person vom Kitchen Table entfernt.")
			return redirect("kitchen_table")

		person_id = request.POST.get("person_id")
		person = None
		if person_id:
			person = get_object_or_404(KitchenTablePerson, pk=person_id, user=request.user)
		form = KitchenTablePersonForm(request.POST, instance=person)
		if form.is_valid():
			person = form.save(commit=False)
			person.user = request.user
			person.save()
			messages.success(request, "Dein Kitchen Table wurde aktualisiert." if person_id else "Zum Kitchen Table hinzugefügt.")
			return redirect("kitchen_table")

		return render(request, self.template_name, {
			"people": KitchenTablePerson.objects.filter(user=request.user),
			"form": form,
		})