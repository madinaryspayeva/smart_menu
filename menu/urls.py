from django.urls import path

from menu.views import (
    MenuPlanCreateView,
    MenuPlanDetailView,
    MenuPlanListView,
    MenuPlanShoppingCartView,
    MenuPlanDeleteView,
)

app_name = "menu"

urlpatterns = [
    path("create/", MenuPlanCreateView.as_view(), name="create"),
    path("<uuid:pk>/", MenuPlanDetailView.as_view(), name="detail"),
    path("<uuid:pk>/cart/", MenuPlanShoppingCartView.as_view(), name="cart"),
    path("list/", MenuPlanListView.as_view(), name="list"),
    path("<uuid:pk>/delete/", MenuPlanDeleteView.as_view(), name="delete"),
]