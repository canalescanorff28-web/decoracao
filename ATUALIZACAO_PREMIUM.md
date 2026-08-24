# Atualização Premium — Aline Naiane & Erika Carina

## O que muda

- Aline Naiane e Erika Carina passam a ser a assinatura principal do site.
- Nova home editorial/luxuosa inspirada em decoração de eventos.
- Hero com galeria de trabalhos reais do catálogo.
- Seção exclusiva das duas decoradoras.
- Portfólio com busca + filtros.
- Cards de projetos redesenhados.
- Carrinho/solicitação mais elegante.
- CTA e botão flutuante de WhatsApp.
- WhatsApp inicial configurado para `5598996127032`.
- Painel admin passa a permitir editar os nomes das decoradoras.
- Seed do catálogo fica não destrutivo: novos deploys não sobrescrevem alterações feitas pelo administrador.
- PWA renomeada para Aline & Erika Decorações.

## Para atualizar no GitHub

Substitua/adicione estes arquivos:

- `templates/catalog/home.html`
- `static/catalog/site.css`
- `static/catalog/site.js`
- `static/catalog/icon-192.svg`
- `static/catalog/icon-512.svg`
- `catalog/models.py`
- `catalog/admin.py`
- `catalog/views.py`
- `catalog/management/commands/seed_catalog.py`
- `catalog/migrations/0002_premium_identity.py` (novo)

Depois faça commit/push na branch `main`. Se o Auto Deploy do Runsite estiver ativo, o serviço será reconstruído e a migration será aplicada pelo `runsite-start.sh`.

## WhatsApp

O número foi normalizado para o formato internacional usado pelo WhatsApp:

`55 + 98 + 996127032 = 5598996127032`

O número continua editável em `/admin/` → Configurações do site.
