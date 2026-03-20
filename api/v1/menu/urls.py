from django.urls import path

from api.v1.menu.views import (
    AddMenuEntryAPIView,
    ClearMenuEntryRecipeAPIView,
    CreateMenuAPIView,
    ShoppingCartAPIView,
    SwapEntriesAPIView,
    UpdateMenuEntryAPIView,
)

app_name = "menu-api"

urlpatterns = [
    path("create/", CreateMenuAPIView.as_view(), name="create"),
    path("swap/", SwapEntriesAPIView.as_view(), name="swap-entries"),
    path("<uuid:plan_id>/cart/", ShoppingCartAPIView.as_view(), name="cart"),
    path("entry/add/", AddMenuEntryAPIView.as_view(), name="add-entry"),
    path("entry/<uuid:entry_id>/", UpdateMenuEntryAPIView.as_view(), name="update-entry"),
    path("entry/<uuid:entry_id>/clear/", ClearMenuEntryRecipeAPIView.as_view(), name="clear-entry"),
]