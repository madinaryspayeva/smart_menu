from django.http import HttpResponse
from django.shortcuts import render
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

from product.mixins import OwnerOrSuperuserMixin
from product.choices import Category
from product.models import Product 
from product.forms import ProductForm


class ProductListView(ListView):
    model = Product
    template_name = "product/list.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-created")

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        if self.request.headers.get("HX-Request"):
            return HttpResponse(
                headers={"HX-Trigger": "productChanged"}
            )
        return response

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        if self.request.headers.get("HX-Request"):
            return render(self.request, self.template_name, context)
        return super().form_invalid(form)

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.choices
        return context


class ProductUpdateView(OwnerOrSuperuserMixin, UpdateView):
    model = Product
    template_name = "product/form.html"
    form_class = ProductForm
    context_object_name = "product"
    success_url = reverse_lazy("product:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.choices
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        if self.request.headers.get("HX-Request"):
            return HttpResponse(
                headers={"HX-Trigger": "productChanged"}
            )
        return response
    
    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        if self.request.headers.get("HX-Request"):
            return render(self.request, self.template_name, context)
        return super().form_invalid(form)


class ProductDeleteView(OwnerOrSuperuserMixin, DeleteView):
    model = Product
    template_name = "product/delete.html"
    success_url = reverse_lazy("product:list")


class ProductDetailView(DetailView):
    model = Product
    template_name = "product/detail.html"
    context_object_name = "product"
