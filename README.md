# Aline Nayane & Érica Carina — Decoração Premium (versão final)

Sistema completo para `https://decoracao.runsite.app`.

## O que está finalizado

- identidade premium com logomarca integrada;
- destaque para Aline Nayane e Érica Carina como decoradoras;
- Instagram das duas com ícones e links;
- catálogo transformado em **portfólio de inspirações**, não produtos fechados;
- cliente pode escolher uma inspiração e informar um tema completamente diferente;
- formulário completo: tema real, tipo de evento, nome, idade, data, local, o que manter e o que adaptar;
- pedido persistido no PostgreSQL/Neon antes de abrir o WhatsApp;
- mensagem do WhatsApp montada automaticamente e enviada para o número configurado no admin;
- modo WhatsApp **100% gratuito via wa.me**, sem Cloud API paga;
- painel `/admin/` com pedidos, status e botões gratuitos de resposta pelo WhatsApp;
- upload de novas fotos pelo admin **salvo no PostgreSQL/Neon**, portanto não depende do disco temporário do Runsite;
- preços, fotos, descrições, publicação, ordem e WhatsApp alteráveis sem editar código;
- seed de catálogo só roda se o catálogo estiver vazio e nunca sobrescreve mudanças feitas no painel;
- PWA e APK continuam apontando para o mesmo site/backend;
- migrations automáticas no deploy do Runsite.

## Atualizar o site já publicado

Substitua o conteúdo do repositório GitHub pela pasta deste projeto e faça commit/push na `main`.
Se o Auto Deploy estiver ligado no Runsite, ele fará o novo deploy sozinho.

O `runsite-start.sh` executa:

```bash
python manage.py migrate --noinput
python manage.py seed_catalog
gunicorn ...
```

As migrations preservam os pedidos e o catálogo que já existem no Neon.

## Depois do deploy

Acesse:

- Site: `https://decoracao.runsite.app`
- Admin: `https://decoracao.runsite.app/admin/`

No admin, abra **Configurações do site** e confira o WhatsApp. O padrão desta versão é `5598996127032`.

## Alterar catálogo sem deploy

No `/admin/` → **Inspirações**:

- adicionar nova inspiração;
- enviar foto do celular/computador;
- mudar preço;
- mudar descrição;
- publicar/despublicar;
- marcar destaque;
- reorganizar.

Essas mudanças entram no Neon e aparecem no site sem novo deploy.

## WhatsApp gratuito

Ao finalizar a solicitação:

1. o backend salva o pedido no Neon;
2. monta a mensagem completa;
3. abre `wa.me` para o número das decoradoras;
4. o cliente apenas confere e toca em **Enviar**.

Não há uso de WhatsApp Cloud API neste modo.
