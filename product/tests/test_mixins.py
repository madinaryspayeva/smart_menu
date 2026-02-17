import pytest
from django.test import RequestFactory
from django.core.exceptions import PermissionDenied
from product.views import ProductUpdateView, ProductDeleteView


@pytest.mark.django_db
class TestOwnerOrSuperUserMixinViews:

    def _get_update_view(self, user, product):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user

        view = ProductUpdateView()
        view.request = request
        view.kwargs = {"pk": product.pk}
        return view

    def _get_delete_view(self, user, product):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user

        view = ProductDeleteView()
        view.request = request
        view.kwargs = {"pk": product.pk}
        return view

    def test_update_view_owner_can_access(self, owner, product):
        view = self._get_update_view(owner, product)
        obj = view.get_object()

        assert obj == product

    def test_update_view_superuser_can_access(self, superuser, product):
        view = self._get_update_view(superuser, product)
        obj = view.get_object()

        assert obj == product

    def test_update_view_other_user_cannot_access(self, other_user, product):
        view = self._get_update_view(other_user, product)

        with pytest.raises(PermissionDenied):
            view.get_object()

    def test_delete_view_owner_can_access(self, owner, product):
        view = self._get_delete_view(owner, product)
        obj = view.get_object()

        assert obj == product

    def test_delete_view_superuser_can_access(self, superuser, product):
        view = self._get_delete_view(superuser, product)
        obj = view.get_object()

        assert obj == product

    def test_delete_view_other_user_cannot_access(self, other_user, product):
        view = self._get_delete_view(other_user, product)

        with pytest.raises(PermissionDenied):
            view.get_object()
