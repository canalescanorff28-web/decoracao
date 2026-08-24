from django.db import migrations, models


def upgrade_existing_settings(apps, schema_editor):
    SiteSettings = apps.get_model("catalog", "SiteSettings")
    settings = SiteSettings.objects.filter(pk=1).first()
    if not settings:
        return

    changed = []
    if not getattr(settings, "owner_whatsapp", ""):
        settings.owner_whatsapp = "5598996127032"
        changed.append("owner_whatsapp")
    if settings.business_name in ("", "Catálogo Decorações"):
        settings.business_name = "Aline & Erika Decorações"
        changed.append("business_name")
    if settings.hero_title in ("", "Decoração que transforma momentos em memórias."):
        settings.hero_title = "Cenários que transformam celebrações em memórias inesquecíveis."
        changed.append("hero_title")
    if changed:
        settings.save(update_fields=changed)


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="decorator_one_name",
            field=models.CharField(default="Aline Naiane", max_length=100),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="decorator_two_name",
            field=models.CharField(default="Erika Carina", max_length=100),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="business_name",
            field=models.CharField(default="Aline & Erika Decorações", max_length=120),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="hero_title",
            field=models.CharField(default="Cenários que transformam celebrações em memórias inesquecíveis.", max_length=220),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="owner_whatsapp",
            field=models.CharField(blank=True, default="5598996127032", help_text="Número que receberá os pedidos. Ex.: 5598999999999", max_length=30),
        ),
        migrations.RunPython(upgrade_existing_settings, migrations.RunPython.noop),
    ]
