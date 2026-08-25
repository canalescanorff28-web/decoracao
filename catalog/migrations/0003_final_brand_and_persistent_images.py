from django.db import migrations, models


def upgrade_identity(apps, schema_editor):
    SiteSettings = apps.get_model("catalog", "SiteSettings")
    site = SiteSettings.objects.filter(pk=1).first()
    if not site:
        return
    changed = []
    if site.decorator_one_name in ("Aline Naiane", "Aline Nayane"):
        site.decorator_one_name = "Aline Nayane"
        changed.append("decorator_one_name")
    if site.decorator_two_name in ("Erika Carina", "Érica Carina"):
        site.decorator_two_name = "Érica Carina"
        changed.append("decorator_two_name")
    if site.owners in ("Aline Naiane & Erika Carina", "Aline Nayane & Érica Carina"):
        site.owners = "Aline Nayane & Érica Carina"
        changed.append("owners")
    if site.business_name in ("Aline & Erika Decorações", "Catálogo Decorações", ""):
        site.business_name = "Aline Nayane & Érica Carina Decoração"
        changed.append("business_name")
    if site.hero_title in (
        "Cenários que transformam celebrações em memórias inesquecíveis.",
        "Decoração que transforma momentos em memórias.",
        "",
    ):
        site.hero_title = "Transformamos inspirações em cenários únicos para momentos inesquecíveis."
        changed.append("hero_title")
    if not site.owner_whatsapp:
        site.owner_whatsapp = "5598984669115"
        changed.append("owner_whatsapp")
    if changed:
        site.save(update_fields=changed)


class Migration(migrations.Migration):
    dependencies = [("catalog", "0002_premium_identity")]
    operations = [
        migrations.AddField(
            model_name="decoration",
            name="image_blob",
            field=models.BinaryField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="decoration",
            name="image_mime",
            field=models.CharField(blank=True, editable=False, max_length=80),
        ),
        migrations.AlterField(
            model_name="decoration",
            name="slug",
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name="decoration",
            name="title",
            field=models.CharField(max_length=180, verbose_name="Nome da inspiração"),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="business_name",
            field=models.CharField(default="Aline Nayane & Érica Carina Decoração", max_length=120),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="decorator_one_name",
            field=models.CharField(default="Aline Nayane", max_length=100),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="decorator_two_name",
            field=models.CharField(default="Érica Carina", max_length=100),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="hero_title",
            field=models.CharField(default="Transformamos inspirações em cenários únicos para momentos inesquecíveis.", max_length=220),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="owners",
            field=models.CharField(default="Aline Nayane & Érica Carina", max_length=180),
        ),
        migrations.RunPython(upgrade_identity, migrations.RunPython.noop),
    ]
