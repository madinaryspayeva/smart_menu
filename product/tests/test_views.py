import json
import pytest
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from product.models import Product
from product.choices import Category


@pytest.mark.django_db
def test_list_view(client, product):
    url = reverse("product:list")
    response = client.get(url)
    assert response.status_code == 200
    assert "products" in response.context
    assert product in response.context["products"]


@pytest.mark.django_db
@pytest.mark.parametrize("query, expected_count", [
    ("App", 1),
    ("Banana", 0),
    ("", 1),
])
def test_list_view_search(client, product, query, expected_count):
    url = reverse("product:list")
    response = client.get(url, {"q": query})
    assert len(response.context["products"]) == expected_count


@pytest.mark.django_db
@pytest.mark.parametrize("sort_param, first_item_name", [
    ("name", "Apple"),
    ("date", "Apple")
])
def test_list_view_sort(client, product, sort_param, first_item_name):
    url = reverse("product:list")
    response = client.get(url, {"sort": sort_param})
    products = list(response.context["products"])
    assert products[0].name == first_item_name


@pytest.mark.django_db
def test_create_view(client, owner):
    client.force_login(owner)
    url = reverse("product:add")
    data = {"name": "Banana", "category": Category.FRUITS}
    response = client.post(url, data)
    assert response.status_code == 302
    assert Product.objects.filter(name="Banana", created_by=owner).exists()


@pytest.mark.django_db
def test_create_view_hx_request(client, owner):
    client.force_login(owner)
    url = reverse("product:add")
    data = {"name": "Orange", "category": Category.FRUITS}
    response = client.post(url, data, HTTP_HX_REQUEST="true")
    assert response.status_code == 200
    assert response.headers.get("HX-Trigger")


@pytest.mark.django_db
def test_update_view_owner(client, product, owner):
    client.force_login(owner)
    url = reverse("product:edit", kwargs={"pk": product.pk})
    data = {"name": "Updated Apple", "category": product.category}
    response = client.post(url, data)
    product.refresh_from_db()
    assert response.status_code == 302
    assert product.name == "Updated Apple"


@pytest.mark.django_db
def test_update_view_superuser(client, product, superuser):
    client.force_login(superuser)
    url = reverse("product:edit", kwargs={"pk": product.pk})
    data = {"name": "Apple Admin", "category": product.category}
    response = client.post(url, data)
    product.refresh_from_db()
    assert response.status_code == 302
    assert product.name == "Apple Admin"


@pytest.mark.django_db
def test_update_view_forbidden(client, product, other_user):
    client.force_login(other_user)
    url = reverse("product:edit", kwargs={"pk": product.pk})
    data = {"name": "Apple other user", "category": product.category}
    response = client.post(url, data)
    assert response.status_code == 403



@pytest.mark.django_db
def test_delete_view(client, product, owner):
    client.force_login(owner)
    url = reverse("product:delete", kwargs={"pk": product.pk})
    response = client.post(url)
    assert response.status_code == 302
    assert not Product.objects.filter(pk=product.pk).exists()


@pytest.mark.django_db
def test_detail_view(client, product):
    url = reverse("product:detail", kwargs={"pk": product.pk})
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["product"] == product


@pytest.mark.django_db
def test_search_view(client, product):
    url = reverse("product:search")
    response = client.get(url, {"q": "App"})
    assert response.status_code == 200
    assert product.name in response.content.decode()


@pytest.mark.django_db
def test_search_filter_view(client, product):
    url = reverse("product:search_filter")
    response = client.get(url, {"q": "App"})
    assert response.status_code == 200
    assert product.name in response.content.decode()