import uuid
from django.shortcuts import render
from django.db.models import Count, Q
from django.views.generic import (
    CreateView, 
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy

from product.models import Product
from recipe.choices import MealType
from recipe.models import Recipe
from recipe.forms import RecipeForm, RecipeIngredientFormSet


class RecipeCreateView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipe/create.html"
    success_url = reverse_lazy("recipe:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.all()
        if self.request.POST:
            context["ingredients"] = RecipeIngredientFormSet(self.request.POST)
        else:
            context["ingredients"] = RecipeIngredientFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["ingredients"]

        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            ingredients = formset.save(commit=False)
            for ingredient in ingredients:
                ingredient.recipe = self.object
                ingredient.save()
            return redirect(self.success_url)
        
        return self.form_invalid(form)

           
class RecipeListView(ListView):
    model = Recipe
    template_name = "recipe/list.html"
    context_object_name = "recipes"
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-created")

        search = self.request.GET.get("q")
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        meal_type = self.request.GET.get("meal_type")
        if meal_type:
            queryset = queryset.filter(meal_type=meal_type)
        
        products_param = self.request.GET.get("products")
        if products_param:
            product_ids = []
            for product_id in products_param.split(","):
                try:
                    uuid_obj = uuid.UUID(product_id)
                    product_ids.append(uuid_obj)
                except (ValueError, AttributeError):
                    continue
            
            if product_ids:
                for product_id in product_ids: #почему здесь цикл можно ли улучшить фтльтрацию?
                    queryset = queryset.filter(ingredient__product_id=product_id)
                
                queryset = queryset.annotate(
                    matching_products=Count("ingredient__product_id", 
                                            filter=Q(ingredient__product_id__in=product_ids)
                                            )
                    ).filter(matching_products=len(product_ids)).distinct()
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meal_types"] = MealType.choices

        selected_products_ids = []
        products_params = self.request.GET.get("products")
        if products_params:
            for product_id in products_params.split(","):
                try:
                    uuid_obj = uuid.UUID(product_id)
                    selected_products_ids.append(uuid_obj)
                except (ValueError, AttributeError):
                    continue

        selected_products = Product.objects.filter(id__in=selected_products_ids)
        context["selected_products"] = selected_products

        context["all_products"] = Product.objects.all()[:50]

        querystring = ""
        if self.request.GET:
            params = self.request.GET.copy()
            if 'page' in params:
                del params['page']
            querystring = params.urlencode()
        context["querystring"] = querystring

        context["has_active_filters"] = bool (
            self.request.GET.get("q") or
            self.request.GET.get("meal_type") or
            self.request.GET.get("products")
        )

        return context




