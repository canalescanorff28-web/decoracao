import orders.models
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("catalog", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(default=orders.models.generate_code, editable=False, max_length=20, unique=True)),
                ("customer_name", models.CharField(max_length=120)),
                ("customer_whatsapp", models.CharField(max_length=30)),
                ("event_date", models.DateField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("consent_whatsapp", models.BooleanField(default=False)),
                ("status", models.CharField(choices=[("RECEBIDO","Recebido"),("ANALISE","Em análise"),("CONFIRMADO","Confirmado"),("FINALIZADO","Finalizado"),("CANCELADO","Cancelado")], default="RECEBIDO", max_length=20)),
                ("total_reference", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("owner_notified", models.BooleanField(default=False)),
                ("customer_notified", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering":["-created_at"]},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title_snapshot", models.CharField(max_length=180)),
                ("unit_price_snapshot", models.DecimalField(decimal_places=2, max_digits=10)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("decoration", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.decoration")),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders.order")),
            ],
        ),
    ]
