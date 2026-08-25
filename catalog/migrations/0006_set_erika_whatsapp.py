from django.db import migrations, models

ERIKA_NUMBER = "5598984673264"

def forwards(apps, schema_editor):
    SiteSettings = apps.get_model("catalog", "SiteSettings")
    site = SiteSettings.objects.first()
    if not site:
        return
    if not site.decorator_two_whatsapp:
        site.decorator_two_whatsapp = ERIKA_NUMBER
        site.save(update_fields=["decorator_two_whatsapp"])

def backwards(apps, schema_editor):
    SiteSettings = apps.get_model("catalog", "SiteSettings")
    site = SiteSettings.objects.first()
    if site and site.decorator_two_whatsapp == ERIKA_NUMBER:
        site.decorator_two_whatsapp = ""
        site.save(update_fields=["decorator_two_whatsapp"])

class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0005_whatsapp_por_decoradora"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="decorator_two_whatsapp",
            field=models.CharField(
                blank=True,
                default=ERIKA_NUMBER,
                help_text="Formato internacional, somente números. Ex.: 5598984673264",
                max_length=30,
                verbose_name="WhatsApp da Érika Carina",
            ),
        ),
        migrations.RunPython(forwards, backwards),
    ]
