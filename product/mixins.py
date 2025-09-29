from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


class OwnerOrSuperuserMixin:
    owner_field = "created_by"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        owner = getattr(obj, self.owner_field)

        if not (self.request.user == owner or self.request.user.is_superuser):
            raise PermissionDenied(_("У вас нет прав на это действие"))
        
        return obj