from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0002_initial"),
    ]

    operations = [
        TrigramExtension(),
    ]
