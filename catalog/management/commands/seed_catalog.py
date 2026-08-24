from django.core.management.base import BaseCommand
from catalog.models import Decoration, SiteSettings

ITEMS = [('Arca de Noé • 1 ano', 'arca-de-noe-1-ano', 'INFANTIL', 'Uma composição alegre em azul, verde, amarelo e laranja, com arco de balões, painéis personalizados e cenografia temática.', '1200.00', 'pagina-03-1.jpeg'), ('Cerejinha', 'cerejinha', 'INFANTIL', 'Decoração delicada e moderna em rosa, vermelho e verde, com cenografia personalizada e detalhes marcantes.', '1300.00', 'pagina-03-2.jpeg'), ('Aniversário Preto & Dourado', 'aniversario-preto-dourado', 'ADULTO', 'Proposta moderna, sofisticada e elegante com preto, dourado e madeira.', '490.00', 'pagina-04-1.jpeg'), ('Festa Adulto', 'festa-adulto', 'ADULTO', 'Cenário em rosa, rosé e dourado para aniversários, bodas, comemorações e eventos adultos.', '600.00', 'pagina-04-2.jpeg'), ('Sonic', 'sonic', 'INFANTIL', 'Festa temática compacta e vibrante em tons de azul e dourado.', '300.00', 'pagina-05-1.jpeg'), ('Circo Rosa', 'circo-rosa', 'INFANTIL', 'Uma montagem lúdica em tons pastel, com arco orgânico de balões e cenografia temática.', '550.00', 'pagina-05-2.jpeg'), ('Aniversários, Celebrações & Eventos', 'aniversarios-celebracoes-eventos', 'EVENTOS', 'Composição impactante em roxo, preto e prata, indicada para celebrações e eventos especiais.', '700.00', 'pagina-06-1.jpeg'), ('Aniversário Branco & Dourado', 'aniversario-branco-dourado', 'ADULTO', 'Decoração clean e elegante em branco e dourado, com painéis, mesas, flores e balões.', '250.00', 'pagina-06-2.jpeg'), ('Ursinha', 'ursinha', 'INFANTIL', 'Cenário delicado em rosa, rosé, branco e dourado, ideal para chá de bebê e chá revelação.', '700.00', 'pagina-07-1.jpeg'), ('Ovelhinha', 'ovelhinha', 'INFANTIL', 'Tema acolhedor em verde, branco, azul e madeira, pensado para chá de bebê e celebrações infantis.', '600.00', 'pagina-07-2.jpeg'), ('Guerreiras do K-pop', 'guerreiras-k-pop', 'INFANTIL', 'Tema moderno e criativo em rosa, roxo e lilás, com elementos personalizados e arco de balões.', '450.00', 'pagina-08-1.jpeg'), ('Safari', 'safari', 'INFANTIL', 'Cenografia safari em verde, marrom, bege e tons naturais, com visual moderno e encantador.', '400.00', 'pagina-08-2.jpeg'), ('Celebração Corporativa', 'celebracao-corporativa', 'EVENTOS', 'Montagem clean em branco e dourado para confraternizações, aniversários e eventos especiais.', '500.00', 'pagina-09-1.jpeg'), ('Aniversário Azul & Dourado', 'aniversario-azul-dourado', 'ADULTO', 'Cenário sofisticado em azul, dourado e branco, com cortina de LED, balões e mobiliário dourado.', '480.00', 'pagina-09-2.jpeg')]

class Command(BaseCommand):
    help = "Cria o catálogo inicial somente quando o banco ainda está vazio."

    def handle(self, *args, **options):
        site = SiteSettings.current()
        changed = []
        if not site.owner_whatsapp:
            site.owner_whatsapp = "5598996127032"
            changed.append("owner_whatsapp")
        if site.business_name in ("", "Catálogo Decorações"):
            site.business_name = "Aline & Erika Decorações"
            changed.append("business_name")
        if site.hero_title in ("", "Decoração que transforma momentos em memórias."):
            site.hero_title = "Cenários que transformam celebrações em memórias inesquecíveis."
            changed.append("hero_title")
        if changed:
            site.save(update_fields=changed)

        # Importante: depois que o dono começar a editar o catálogo pelo admin,
        # novos deploys NÃO podem restaurar preços ou itens do catálogo de exemplo.
        if Decoration.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Catálogo já possui itens; seed inicial ignorado para preservar as edições do painel."
            ))
            return

        for order, row in enumerate(ITEMS, start=1):
            title, slug, category, desc, price, image = row
            Decoration.objects.create(
                title=title,
                slug=slug,
                category=category,
                description=desc,
                price=price,
                image_path=f"catalog/images/{image}",
                active=True,
                display_order=order,
                featured=order <= 4,
            )
        self.stdout.write(self.style.SUCCESS("Catálogo inicial criado."))
