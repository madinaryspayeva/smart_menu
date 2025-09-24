from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy 
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    ListView,
    DetailView
)

from product.models import Product
from product.forms import ProductForm


class ProductListView(ListView):
    model = Product
    template_name = "product/list.html"
    context_object_name = "products"


class ProductCreateView(CreateView):
    model = Product
    template_name = "product/form.html"
    form_class = ProductForm
    success_url = reverse_lazy("product:list")


    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UpdateView):
    model = Product
    template_name = "product/form.html"
    form_class = ProductForm
    context_object_name = "product"
    success_url = reverse_lazy("product:list")
    

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.created_by != self.request.user:
            raise PermissionDenied(_("Нельзя редактировать чужие продукты."))
        return obj


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "product/delete.html"
    success_url = reverse_lazy("product:list")


    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.created_by != self.request.user:
            raise PermissionDenied(_("Нельзя удалить чужие продукты."))
        return obj


class ProductDetailView(DetailView):
    model = Product
    template_name = "product/detail.html"
    context_object_name = "product"

