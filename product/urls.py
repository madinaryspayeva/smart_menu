from django.urls import path
from product.views import (
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView
)

app_name = 'product'

urlpatterns = [
    path("", ProductListView.as_view(), name="list"),
    path("product/add/", ProductCreateView.as_view(), name="add"),
    path("/<int:pk>/edit/", ProductUpdateView.as_view(), name="edit"),
    path("/<int:pk>/delete/", ProductDeleteView.as_view(), name="delete"),
]
