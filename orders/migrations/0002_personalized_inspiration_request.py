from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("orders", "0001_initial")]
    operations = [
        migrations.AddField(model_name="order", name="event_type", field=models.CharField(blank=True, choices=[("ANIVERSARIO", "Aniversário"), ("CHÁ", "Chá / Revelação / Bebê"), ("CASAMENTO", "Casamento / Bodas"), ("CORPORATIVO", "Evento corporativo"), ("OUTRO", "Outro")], max_length=30, verbose_name="Tipo de evento")),
        migrations.AddField(model_name="order", name="event_theme", field=models.CharField(blank=True, max_length=180, verbose_name="Tema real da festa")),
        migrations.AddField(model_name="order", name="celebrant_name", field=models.CharField(blank=True, max_length=120, verbose_name="Nome do aniversariante / homenageado")),
        migrations.AddField(model_name="order", name="celebrant_age", field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Idade")),
        migrations.AddField(model_name="order", name="event_location", field=models.CharField(blank=True, max_length=220, verbose_name="Local do evento")),
        migrations.AddField(model_name="order", name="keep_details", field=models.TextField(blank=True, verbose_name="O que quer manter da inspiração")),
        migrations.AddField(model_name="order", name="change_details", field=models.TextField(blank=True, verbose_name="O que quer adaptar / mudar")),
        migrations.AlterField(model_name="order", name="notes", field=models.TextField(blank=True, verbose_name="Outras observações")),
    ]
