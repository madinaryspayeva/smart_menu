from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from product.models import Product
from product.choices import Category
from product.views import ProductUpdateView, ProductDeleteView


User = get_user_model()


class OwnerOrSuperUserMixinViewsTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.owner = User.objects.create_user(email="owner@example.com", password="securepass")
        self.superuser = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.other_user = User.objects.create_user(email="otheruser@example.com", password="securepass")
        self.product = Product.objects.create(name="Apple", category=Category.FRUITS, created_by=self.owner)
        
    def _get_update_view(self, user):
        request = self.factory.get("/")
        request.user = user
        view = ProductUpdateView()
        view.request = request
        view.kwargs = {"pk": self.product.pk}
        return view
    
    def _get_delete_view(self, user):
        request = self.factory.get("/")
        request.user = user
        view = ProductDeleteView()
        view.request = request
        view.kwargs = {"pk": self.product.pk}
        return view 
    
    def test_update_view_owner_can_access(self):
        view = self._get_update_view(self.owner)
        obj = view.get_object()
        self.assertEqual(obj, self.product)
    
    def test_update_view_superuser_can_access(self):
        view = self._get_update_view(self.superuser)
        obj = view.get_object()
        self.assertEqual(obj, self.product) 
    
    def test_update_view_other_user_cannot_access(self):
        view = self._get_update_view(self.other_user)
        with self.assertRaises(PermissionDenied):
            view.get_object()
    
    def test_delete_view_owner_can_access(self):
        view = self._get_delete_view(self.owner)
        obj = view.get_object()
        self.assertEqual(obj, self.product)

    def test_delete_view_superuser_can_access(self):
        view = self._get_delete_view(self.superuser)
        obj = view.get_object()
        self.assertEqual(obj, self.product)

    def test_delete_view_other_user_cannot_access(self):
        view = self._get_delete_view(self.other_user)
        with self.assertRaises(PermissionDenied):
            view.get_object()
