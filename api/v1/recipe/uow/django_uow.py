from django.db import transaction

from api.v1.recipe.interfaces.uow import IUnitOfWork



class DjangoUnitOfWork(IUnitOfWork):

    def __enter__(self):
        self._transaction = transaction.atomic()
        self._transaction.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._transaction.__exit__(exc_type, exc_val, exc_tb)
