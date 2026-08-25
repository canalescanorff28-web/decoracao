# V8.3 — emojis no WhatsApp Web

## Diagnóstico final
O código Python, JSON e percent-encoding estavam corretos, mas o endpoint
intermediário `api.whatsapp.com/send` continuava exibindo caracteres de
substituição (`�`) no ambiente de WhatsApp Web do usuário.

## Mudança
O endpoint intermediário foi removido.

Agora:
- desktop -> `https://web.whatsapp.com/send?...`
- celular -> `whatsapp://send?...`

A mensagem continua:
- montada no servidor;
- codificada explicitamente em UTF-8;
- percent-encoded;
- fora de headers HTTP grandes;
- sem passagem pelo JavaScript.

## Compatibilidade
A página intermediária detecta desktop/celular e possui dois botões manuais:
- Abrir no WhatsApp Web
- Abrir no aplicativo

O campo legado `owner_whatsapp_link` agora aponta para a própria rota interna
do pedido, evitando que versões antigas do JavaScript voltem a usar URLs
externas com a mensagem completa.
