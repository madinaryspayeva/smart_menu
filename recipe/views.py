from django.shortcuts import render
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
        
        #добавить поиск по ингредиентам

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meal_types"] = MealType.choices
        return context




