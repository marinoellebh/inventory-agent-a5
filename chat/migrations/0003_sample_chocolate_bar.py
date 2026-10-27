from decimal import Decimal

from django.db import migrations


def add_sample_item(apps, schema_editor):
    Item = apps.get_model("chat", "Item")
    if not Item.objects.filter(name__iexact="Chocolate bar").exists():
        Item.objects.create(name="Chocolate bar", quantity=10, price=Decimal("2.50"))


class Migration(migrations.Migration):
    dependencies = [("chat", "0002_item_price")]
    operations = [migrations.RunPython(add_sample_item, migrations.RunPython.noop)]
