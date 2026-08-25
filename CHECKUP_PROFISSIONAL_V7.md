# CHECK-UP PROFISSIONAL V7

Base analisada: `canalescanorff28-web/decoracao` / branch `main`.

## CRÍTICO — corrigido
- `seed_catalog` usava `changed.append()` antes de `changed = []`, capaz de interromper novo deploy no Runsite.
- mensagem do WhatsApp usava `"\\n".join(...)`, gerando `\n` literal no texto.
- testes antigos não executavam o seed e, por isso, não detectavam essa regressão.

## ALTO — corrigido
- CTA ainda dependia do campo legado `owner_whatsapp`; agora usa os dois WhatsApps reais.
- números de Aline e Érika ficam separados e editáveis no admin.
- padronização de marca para `Aline Nayane & Érika Carina`.
- service worker não intercepta nem armazena `/admin/` ou `/api/`.
- produção passa a exigir `SECRET_KEY` e `DATABASE_URL`.
- endpoint público de status deixa de expor nome/tema do cliente.
- consentimento de WhatsApp validado também no backend.
- data passada, tipo de evento inválido e seleção stale passam a ser rejeitados.

## MÉDIO — corrigido
- código de pedido novo passa de 24 para 40 bits de entropia.
- índices para status, data do evento e criação dos pedidos.
- upload de imagem validado com Pillow, redimensionado e convertido para WebP.
- imagem do catálogo recebe versionamento por `updated_at`, evitando foto velha em cache.
- `robots.txt`, `sitemap.xml`, canonical, Open Graph, Twitter Card e JSON-LD.
- navegação móvel própria, skip link, foco visível e suporte a `prefers-reduced-motion`.
- leitura de carrinho em localStorage tolera dados corrompidos.
- honeypot simples contra bots, sem serviço pago.
- PWA usa cache mais seguro e versão `v8`.
- toggle `enabled` passa a mostrar manutenção real quando desativado.

## CI / QA — melhorado
O workflow agora verifica:
- `manage.py check`;
- migrations esquecidas;
- sintaxe JavaScript;
- `seed_catalog` duas vezes;
- testes Django;
- `collectstatic`.

Também foram adicionados testes para:
- ambos os WhatsApps;
- regressão de `\n` literal;
- emojis/Unicode;
- proteção de dados no status;
- consentimento;
- data passada;
- honeypot;
- service worker;
- robots/sitemap;
- preservação do catálogo no seed.

## Limitação desta sessão
A URL do Runsite não pôde ser carregada diretamente pelas ferramentas disponíveis. A comparação foi feita contra a `main` real do GitHub, commits recentes, GitHub Actions e os vídeos/prints fornecidos.


## Validação estática desta entrega
- 34 arquivos Python analisados por AST: OK
- JavaScript validado com `node --check`: OK
- balanço de tags Django condicionais/form/dialog: OK
- regressões críticas do seed, WhatsApp e service worker: verificadas.

O teste Django completo fica a cargo do GitHub Actions, pois Django não está instalado no runtime local desta sessão.
