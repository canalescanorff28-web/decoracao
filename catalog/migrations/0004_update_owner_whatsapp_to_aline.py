from django.db import migrations

OLD_NUMBER = "5598996127032"
NEW_NUMBER = "5598984669115"

def forwards(apps, schema_editor):
    SiteSettings = apps.get_model("catalog", "SiteSettings")
    site = SiteSettings.objects.first()
    if not site:
        return
    if not site.owner_whatsapp or site.owner_whatsapp == OLD_NUMBER:
        site.owner_whatsapp = NEW_NUMBER
        site.save(update_fields=["owner_whatsapp"])

def backwards(apps, schema_editor):
    SiteSettings = apps.get_model("catalog", "SiteSettings")
    site = SiteSettings.objects.first()
    if not site:
        return
    if site.owner_whatsapp == NEW_NUMBER:
        site.owner_whatsapp = OLD_NUMBER
        site.save(update_fields=["owner_whatsapp"])

class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0003_final_brand_and_persistent_images"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
