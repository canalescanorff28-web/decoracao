# V8.2 — correção do 5xx no handoff para WhatsApp

## Sintoma
Ao escolher Aline ou Érika, a rota:
`/api/orders/DEC-.../whatsapp/erika/`
podia retornar `upstream 5xx` no Runsite.

## Causa
A V8.1 respondia com HTTP 302 e colocava a URL completa do WhatsApp no header
`Location`.

Como a mensagem possui muitos campos, acentos, emojis e quebras de linha, a URL
percent-encoded pode chegar a vários KB. Proxies/reverse proxies podem impor
limites menores para um único header e rejeitar a resposta.

## Correção
A rota agora responde `200 OK` com uma página HTML curta.

A URL longa:
- fica no corpo da resposta;
- não fica em `Location`;
- continua 100% percent-encoded em UTF-8;
- é aberta automaticamente por JavaScript;
- possui botão `Abrir WhatsApp agora` como fallback.

Isso preserva:
- emojis;
- quebras de linha;
- Aline/Érika;
- WhatsApp Web;
- WhatsApp no celular.

Nenhuma API paga foi adicionada.
