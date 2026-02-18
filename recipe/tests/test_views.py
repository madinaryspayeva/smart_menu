import pytest
from django.urls import reverse
from recipe.choices import MealType, Unit
from recipe.models import Recipe


@pytest.mark.django_db
class TestRecipeCreateView:

    def test_create_recipe_success(self, client, owner, recipe_source, product):
        client.force_login(owner)

        url = reverse("recipe:add")
            
        data = {
            "name": "Омлет",
            "description": "Описание",
            "meal_type": MealType.BREAKFAST.value,
            "source": recipe_source.id,
            "servings": 2,

            # management form
            "ingredient-TOTAL_FORMS": "1",
            "ingredient-INITIAL_FORMS": "0",
            "ingredient-MIN_NUM_FORMS": "0",
            "ingredient-MAX_NUM_FORMS": "1000",

            # поля formset
            "ingredient-0-product": str(product.id),
            "ingredient-0-quantity": "100",
            "ingredient-0-unit": Unit.GR.value,
        }

        response = client.post(url, data)

        assert response.status_code == 302
        assert Recipe.objects.filter(name="Омлет", created_by=owner).exists()


@pytest.mark.django_db
class TestRecipeUpdateView:

    def test_owner_can_update(self, client, owner, recipe, ingredient):
        recipe.created_by = owner
        recipe.save()

        client.force_login(owner)

        url = reverse("recipe:edit", kwargs={"pk": recipe.pk})

        data = {
           "name": "Обновленный рецепт",
            "description": recipe.description,
            "meal_type": recipe.meal_type,
            "source": recipe.source.id if recipe.source else "",
            "servings": recipe.servings or 1,

           
            # management form
            "ingredient-TOTAL_FORMS": "1",
            "ingredient-INITIAL_FORMS": "1",
            "ingredient-MIN_NUM_FORMS": "0",
            "ingredient-MAX_NUM_FORMS": "1000",

            # поля formset
            "ingredient-0-id": str(ingredient.id),
            "ingredient-0-product": str(ingredient.product.id),
            "ingredient-0-quantity": str(ingredient.quantity),
            "ingredient-0-unit": ingredient.unit,
        }

        response = client.post(url, data)
        
        recipe.refresh_from_db()

        assert response.status_code == 302
        assert recipe.name == "Обновленный рецепт"
    
    def test_other_user_cannot_update(self, client, other_user, recipe):
        client.force_login(other_user)

        url = reverse("recipe:edit", kwargs={"pk": recipe.pk})
        response = client.get(url)

        assert response.status_code == 403

@pytest.mark.django_db
class TestRecipeDeleteView:

    def test_owner_can_delete(self, client, owner, recipe):
        recipe.created_by = owner
        recipe.save()

        client.force_login(owner)

        url = reverse("recipe:delete", kwargs={"pk": recipe.pk})
        response = client.post(url)

        assert response.status_code == 302
        assert not Recipe.objects.filter(pk=recipe.pk).exists()


@pytest.mark.django_db
class TestRecipeDetailView:

    def test_detail_view(self, client, recipe):
        url = reverse("recipe:detail", kwargs={"pk": recipe.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["recipe"] == recipe


@pytest.mark.django_db
class TestRecipeListView:

    def test_list_view(self, client, recipe):
        url = reverse("recipe:list")
        response = client.get(url)

        assert response.status_code == 200
        assert recipe in response.context["recipes"]
    
    def test_search_filter(self, client, recipe):
        recipe.name = "Суп"
        recipe.save()

        url = reverse("recipe:list")
        response = client.get(url, {"q": "Суп"})

        assert response.status_code == 200
        assert recipe in response.context["recipes"]

    def test_meal_type_filter(self, client, recipe):
        url = reverse("recipe:list")
        response = client.get(url, {"meal_type": recipe.meal_type})

        assert recipe in response.context["recipes"]
    
    def test_product_filter(self, client, recipe_factory, product, product_1):
       
        recipe_with_product = recipe_factory(
        name="С яблоком",
        products=[product]
        )
        recipe_without_product = recipe_factory(
            name="С молоком",
            products=[product_1]
        )

        url = reverse("recipe:list")
        response = client.get(url, {"products": str(product.id)})

        recipes = response.context["recipes"]

        assert recipe_with_product in recipes
        assert recipe_without_product not in recipes
    
    def test_has_active_filters_flag(self, client, recipe):
        url = reverse("recipe:list")
        response = client.get(url, {"q": "test"})

        assert response.context["has_active_filters"] is True
            