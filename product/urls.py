from django.urls import path
from .views import (
    ProductListView,
    ProductCreateView,
    ProductDetailView,
    ProductUpdateView,
    ProductDeleteView,
    ProductSearchView,
    ProductSearchFilterView
)

app_name = "product"

urlpatterns = [
    path("", ProductListView.as_view(), name="list"),
    path("add/", ProductCreateView.as_view(), name="add"),
    path("<uuid:pk>/", ProductDetailView.as_view(), name="detail"),
    path("<uuid:pk>/edit/", ProductUpdateView.as_view(), name="edit"),
    path("<uuid:pk>/delete/", ProductDeleteView.as_view(), name="delete"),
    path("search/", ProductSearchView.as_view(), name="search"),
    path("search_filter/", ProductSearchFilterView.as_view(), name="search_filter")
]