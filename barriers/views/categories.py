from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, View

from utils.metadata import MetadataMixin

from ..forms.categories import AddCategoryForm, EditCategoriesForm
from .mixins import BarrierMixin


class AddCategory(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/categories/add.html"
    form_class = AddCategoryForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({"categories": self.get_category_list()})
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["categories"] = self.get_category_list()
        return kwargs

    def get_category_list(self):
        """
        Get a list of all categories excluding any already selected
        """
        selected_category_ids = [
            str(category["id"])
            for category in self.request.session.get("categories", [])
        ]
        return [
            category
            for category in self.metadata.get_category_list()
            if str(category["id"]) not in selected_category_ids
        ]

    def form_valid(self, form):
        """
        Add the new category to the session and redirect
        """
        category = self.metadata.get_category(form.cleaned_data["category"])
        categories = self.request.session.get("categories", [])
        categories.append(
            {"id": category["id"], "title": category["title"],}
        )
        self.request.session["categories"] = categories
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:edit_categories_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierEditCategories(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/categories/edit.html"
    form_class = EditCategoriesForm
    use_session_categories = False

    def get(self, request, *args, **kwargs):
        if not self.use_session_categories:
            request.session["categories"] = self.barrier.categories
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {"categories": self.request.session.get("categories", [])}
        )
        return context_data

    def get_initial(self):
        categories = self.request.session.get("categories", [])
        return {
            "categories": [category["id"] for category in categories],
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier_id"] = str(self.kwargs.get("barrier_id"))
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["categories"] = self.metadata.get_category_list()
        return kwargs

    def form_valid(self, form):
        form.save()
        try:
            del self.request.session["categories"]
        except KeyError:
            pass
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierEditCategoriesSession(BarrierEditCategories):
    use_session_categories = True


class BarrierRemoveCategory(View):
    """
    Remove the category from the session and redirect
    """

    def post(self, request, *args, **kwargs):
        categories = self.request.session.get("categories", [])
        category_id = request.POST.get("category_id")

        self.request.session["categories"] = [
            category
            for category in categories
            if category_id != str(category["id"])
        ]
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "barriers:edit_categories_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
