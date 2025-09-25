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

from product.choices import Category
from product.models import Product 
from product.forms import ProductForm


class ProductListView(ListView):
    model = Product
    template_name = "product/list.html"
    context_object_name = "products"
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()

        search = self.request.GET.get("q")
        if search:
            queryset = queryset.filter(name__icontains=search)

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        sort = self.request.GET.get("sort")
        if sort == "name":
            queryset = queryset.order_by("name")
        elif sort == "date":
            queryset = queryset.order_by("-created")
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.choices
        return context


class ProductCreateView(CreateView):
    model = Product
    template_name = "product/form.html"
    form_class = ProductForm
    success_url = reverse_lazy("product:list")


    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.choices
        return context


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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.choices
        return context


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "product/delete.html"
    success_url = reverse_lazy("product:list")


    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.created_by != self.request_user:
            raise PermissionDenied(_("Нельзя удалить чужие продукты."))
        return obj


class ProductDetailView(DetailView):
    model = Product
    template_name = "product/detail.html"
    context_object_name = "product"
