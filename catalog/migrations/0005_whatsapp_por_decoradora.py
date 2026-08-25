from django.db import migrations, models

OLD_USER_NUMBER = "5598996127032"
ALINE_NUMBER = "5598984669115"

def forwards(apps, schema_editor):
    SiteSettings = apps.get_model("catalog", "SiteSettings")
    site = SiteSettings.objects.first()
    if not site:
        return

    # Remove o número pessoal antigo do fluxo.
    if site.owner_whatsapp == OLD_USER_NUMBER:
        site.owner_whatsapp = ""

    if not site.decorator_one_whatsapp:
        site.decorator_one_whatsapp = ALINE_NUMBER

    site.save(update_fields=[
        "owner_whatsapp",
        "decorator_one_whatsapp",
        "decorator_two_whatsapp",
    ])

def backwards(apps, schema_editor):
    SiteSettings = apps.get_model("catalog", "SiteSettings")
    site = SiteSettings.objects.first()
    if not site:
        return
    if not site.owner_whatsapp:
        site.owner_whatsapp = OLD_USER_NUMBER
        site.save(update_fields=["owner_whatsapp"])

class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0004_update_owner_whatsapp_to_aline"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="decorator_one_whatsapp",
            field=models.CharField(
                blank=True,
                default=ALINE_NUMBER,
                help_text="Formato internacional, somente números. Ex.: 5598984669115",
                max_length=30,
                verbose_name="WhatsApp da Aline Nayane",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="decorator_two_whatsapp",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Formato internacional, somente números. Cadastre para aparecer como opção no site.",
                max_length=30,
                verbose_name="WhatsApp da Érika Carina",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="owner_whatsapp",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Campo legado. O atendimento usa os WhatsApps individuais abaixo.",
                max_length=30,
            ),
        ),
        migrations.RunPython(forwards, backwards),
    ]
