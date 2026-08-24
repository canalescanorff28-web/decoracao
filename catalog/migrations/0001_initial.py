from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Decoration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("slug", models.SlugField(unique=True)),
                ("category", models.CharField(choices=[("INFANTIL","Infantil"),("ADULTO","Adulto"),("EVENTOS","Eventos")], max_length=20)),
                ("description", models.TextField(blank=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("image_path", models.CharField(blank=True, help_text="Caminho dentro de static. Ex.: catalog/images/pagina-03-1.jpeg", max_length=255)),
                ("image_url", models.URLField(blank=True)),
                ("active", models.BooleanField(default=True)),
                ("featured", models.BooleanField(default=False)),
                ("display_order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering":["display_order","title"]},
        ),
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("business_name", models.CharField(default="Catálogo Decorações", max_length=120)),
                ("owners", models.CharField(default="Aline Naiane & Erika Carina", max_length=180)),
                ("hero_title", models.CharField(default="Decoração que transforma momentos em memórias.", max_length=220)),
                ("owner_whatsapp", models.CharField(blank=True, help_text="Número que receberá os pedidos. Ex.: 5598999999999", max_length=30)),
                ("instagram_one", models.CharField(blank=True, default="@aline.naiane.35", max_length=100)),
                ("instagram_two", models.CharField(blank=True, default="@erikacarin_decor", max_length=100)),
                ("enabled", models.BooleanField(default=True)),
            ],
            options={"verbose_name":"Configuração do site","verbose_name_plural":"Configurações do site"},
        ),
    ]
