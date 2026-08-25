from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0002_personalized_inspiration_request"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("RECEBIDO", "Recebido"),
                    ("ANALISE", "Em análise"),
                    ("CONFIRMADO", "Confirmado"),
                    ("FINALIZADO", "Finalizado"),
                    ("CANCELADO", "Cancelado"),
                ],
                db_index=True,
                default="RECEBIDO",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="event_date",
            field=models.DateField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name="Data do evento",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                db_index=True,
                verbose_name="Criado em",
            ),
        ),
    ]
