# Catálogo Decor — Runsite + Neon + WhatsApp + Android

Sistema público de catálogo e solicitações de decoração.

## Arquitetura escolhida

- **GitHub:** repositório principal, histórico, testes e geração do APK.
- **Runsite.app:** hospeda o site e o backend Django.
- **Neon:** PostgreSQL para catálogo, pedidos, clientes e status.
- **Django Admin:** painel privado em `/admin/`.
- **WhatsApp:** recebimento do pedido e automações opcionais via WhatsApp Business Cloud API.
- **PWA:** instalação pelo navegador.
- **Android:** wrapper Capacitor e APK gerado pelo GitHub Actions.

## Fluxo

```text
Cliente / APK
      │
      ▼
https://SEU-PROJETO.runsite.app
      │
      ▼
Runsite Web Service (Django)
      │
      ├──── Neon PostgreSQL
      │
      └──── WhatsApp Business Cloud API
```

## Publicar no Runsite

### 1. Coloque o projeto no GitHub

Envie todos os arquivos deste projeto para a branch `main`.

### 2. No Runsite

Crie um projeto e escolha **Web Service**.

Conecte o repositório do GitHub.

O projeto contém `Dockerfile`, então o Runsite deve construir usando esse arquivo.

Configuração:
- **Port:** `8080`
- **Health check:** `/api/health/`
- **Branch:** `main`
- **Auto deploy:** ativado

O servidor inicia ouvindo em `0.0.0.0:8080`.

### 3. Variáveis de ambiente

Cadastre no Runsite:

- `SECRET_KEY` = chave forte e aleatória
- `DEBUG` = `0`
- `DATABASE_URL` = conexão PostgreSQL do Neon
- `ALLOWED_HOSTS` = `.runsite.app`
- `CSRF_TRUSTED_ORIGINS` = `https://*.runsite.app`
- `PUBLIC_SITE_URL` = URL final fornecida pelo Runsite
- `PORT` = `8080`

Para WhatsApp automático:
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_GRAPH_VERSION`
- `WHATSAPP_AUTO_SEND=1`

Nunca coloque senhas ou tokens diretamente no GitHub.

## Primeiro acesso ao admin

Depois que o deploy estiver online, abra o Shell do serviço no Runsite e execute:

```bash
python manage.py createsuperuser
```

Depois acesse:

```text
https://SEU-PROJETO.runsite.app/admin/
```

No painel você poderá:
- cadastrar e editar decorações;
- alterar preços;
- ativar/desativar itens;
- configurar o WhatsApp do responsável;
- acompanhar pedidos;
- mudar status;
- consultar clientes.

## Número do WhatsApp do responsável

Não precisa alterar código.

Entre em:

`/admin/` → **Configurações do site**

e coloque o número no formato internacional:

```text
5598999999999
```

## Neon

Mantenha a connection string somente na variável `DATABASE_URL` do Runsite.

O banco guarda:
- catálogo;
- pedidos;
- dados de contato informados pelo cliente;
- itens selecionados;
- total de referência;
- status;
- timestamps.

## APK Android

O GitHub Actions continua responsável pelo APK.

No GitHub:
1. Settings
2. Secrets and variables
3. Actions
4. Variables
5. Crie `SITE_URL`
6. Valor: `https://SEU-PROJETO.runsite.app`

Depois:
1. Actions
2. `Android APK`
3. `Run workflow`
4. Baixe `catalogo-decor-apk`

Site, PWA e APK usam o mesmo backend no Runsite.

## Atualizações futuras

O fluxo fica:

```text
Alteração no código
      ↓
GitHub main
      ↓
Runsite auto-deploy
      ↓
Site atualizado
```

Para alterações somente de catálogo, preço ou pedidos, use o `/admin/`; não precisa gerar novo APK.
