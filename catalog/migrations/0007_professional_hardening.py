from django.db import migrations, models
from django.utils import timezone


def normalize_brand(apps, schema_editor):
    SiteSettings = apps.get_model("catalog", "SiteSettings")
    site = SiteSettings.objects.first()
    if not site:
        return

    changed = []

    if site.decorator_two_name in {"Erika Carina", "Érica Carina"}:
        site.decorator_two_name = "Érika Carina"
        changed.append("decorator_two_name")

    if site.owners in {
        "Aline Nayane & Érica Carina",
        "Aline Nayane & Erika Carina",
    }:
        site.owners = "Aline Nayane & Érika Carina"
        changed.append("owners")

    if site.business_name in {
        "Aline Nayane & Érica Carina Decoração",
        "Aline Nayane & Erika Carina Decoração",
    }:
        site.business_name = "Aline Nayane & Érika Carina Decoração"
        changed.append("business_name")

    if changed:
        site.save(update_fields=changed)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0006_set_erika_whatsapp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="business_name",
            field=models.CharField(
                default="Aline Nayane & Érika Carina Decoração",
                max_length=120,
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="owners",
            field=models.CharField(
                default="Aline Nayane & Érika Carina",
                max_length=180,
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="decorator_two_name",
            field=models.CharField(
                default="Érika Carina",
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name="decoration",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True,
                default=timezone.now,
                verbose_name="Atualizada em",
            ),
            preserve_default=False,
        ),
        migrations.RunPython(normalize_brand, migrations.RunPython.noop),
    ]
