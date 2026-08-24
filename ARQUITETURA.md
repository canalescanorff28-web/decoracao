# Arquitetura final — Runsite

```text
                      ┌─────────────────┐
                      │     GitHub      │
                      │ código + Actions│
                      └───────┬─────────┘
                              │ push / deploy
                              ▼
                    ┌─────────────────────┐
                    │     RUNSITE.APP     │
                    │ Web Service Django  │
                    │ Site + API + Admin  │
                    └───────┬─────┬───────┘
                            │     │
                    SQL/TLS │     │ HTTPS API
                            ▼     ▼
                    ┌──────────┐  ┌──────────────┐
                    │   Neon   │  │   WhatsApp   │
                    │PostgreSQL│  │ Business API │
                    └──────────┘  └──────────────┘
                            ▲
                            │
                  ┌─────────┴──────────┐
                  │                    │
             Site público          APK Android
          *.runsite.app          GitHub Actions
```

## Responsabilidades

### Runsite
- URL pública
- HTTPS
- execução do Django/Gunicorn
- endpoints da API
- painel `/admin/`
- deploy automático a partir do GitHub

### Neon
- dados persistentes
- catálogo
- pedidos
- clientes
- status e histórico

### GitHub
- código-fonte
- versionamento
- testes
- geração de APK
- origem dos deploys do Runsite

### WhatsApp
- pedido do cliente para o responsável
- confirmação e atualizações automáticas quando a Cloud API estiver configurada
