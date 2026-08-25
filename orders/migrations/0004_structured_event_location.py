from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0003_professional_indexes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="event_location",
            field=models.CharField(
                blank=True,
                max_length=500,
                verbose_name="Resumo do local do evento",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="event_venue",
            field=models.CharField(blank=True, max_length=120, verbose_name="Nome / tipo do local"),
        ),
        migrations.AddField(
            model_name="order",
            name="event_city",
            field=models.CharField(blank=True, max_length=120, verbose_name="Cidade"),
        ),
        migrations.AddField(
            model_name="order",
            name="event_state",
            field=models.CharField(blank=True, max_length=80, verbose_name="Estado / UF"),
        ),
        migrations.AddField(
            model_name="order",
            name="event_neighborhood",
            field=models.CharField(blank=True, max_length=120, verbose_name="Bairro"),
        ),
        migrations.AddField(
            model_name="order",
            name="event_street",
            field=models.CharField(blank=True, max_length=180, verbose_name="Rua / Avenida"),
        ),
        migrations.AddField(
            model_name="order",
            name="event_number",
            field=models.CharField(blank=True, max_length=40, verbose_name="Número"),
        ),
        migrations.AddField(
            model_name="order",
            name="event_complement",
            field=models.CharField(blank=True, max_length=120, verbose_name="Complemento"),
        ),
        migrations.AddField(
            model_name="order",
            name="event_reference",
            field=models.CharField(blank=True, max_length=180, verbose_name="Ponto de referência"),
        ),
        migrations.AddField(
            model_name="order",
            name="event_postcode",
            field=models.CharField(blank=True, max_length=20, verbose_name="CEP"),
        ),
        migrations.AddField(
            model_name="order",
            name="event_latitude",
            field=models.DecimalField(blank=True, decimal_places=7, editable=False, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="event_longitude",
            field=models.DecimalField(blank=True, decimal_places=7, editable=False, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="guest_count",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Quantidade de convidados"),
        ),
        migrations.AddField(
            model_name="order",
            name="keep_choices",
            field=models.JSONField(blank=True, default=list, verbose_name="Itens que deseja manter"),
        ),
        migrations.AddField(
            model_name="order",
            name="change_choices",
            field=models.JSONField(blank=True, default=list, verbose_name="Itens que deseja adaptar"),
        ),
    ]
