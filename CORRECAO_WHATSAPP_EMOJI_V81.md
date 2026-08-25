# V8.1 — correção estrutural de emojis no WhatsApp

## Diagnóstico
Os arquivos da `main` já continham emojis válidos em UTF-8 e o backend já
gerava percent-encoding. Mesmo assim, no ambiente do usuário, o handoff
navegador → `wa.me` → WhatsApp substituía caracteres de 4 bytes por `�`.

Acentos e símbolos como `━` continuavam funcionando, reforçando que o problema
estava especificamente no transporte/abertura dos emojis, não no catálogo.

## Correção
A mensagem completa não trafega mais pelo JavaScript no fluxo novo.

Fluxo agora:
1. pedido é salvo;
2. frontend recebe somente rotas ASCII curtas:
   `/api/orders/DEC-.../whatsapp/aline/`
   `/api/orders/DEC-.../whatsapp/erika/`
3. cliente escolhe a decoradora;
4. Django lê o pedido do banco;
5. Django recompõe a mensagem;
6. Django serializa a query explicitamente em UTF-8;
7. resposta 302 aponta para o endpoint oficial gratuito:
   `https://api.whatsapp.com/send?...`

O endpoint `api.whatsapp.com/send` usado aqui é apenas o link oficial de
abertura do WhatsApp. Não é a WhatsApp Cloud API e não gera cobrança.

## Proteções de regressão
Os testes verificam:
- `🌸` → `%F0%9F%8C%B8`;
- `✨` → `%E2%9C%A8`;
- quebra de linha → `%0A`;
- ausência de `%EF%BF%BD` (replacement char `�`);
- número correto de Aline e Érika;
- contato geral também passa pelo servidor.
