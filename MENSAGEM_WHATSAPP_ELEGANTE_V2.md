# Mensagem WhatsApp elegante V2

Correções:
- remove `\n` literal;
- usa quebras de linha reais;
- remove asteriscos/markdown para evitar `\*` no texto;
- mantém emojis em Unicode;
- `JsonResponse` usa `ensure_ascii=False`;
- aplica o mesmo padrão a qualquer decoração;
- melhora mensagens de recebido, confirmado e finalizado;
- inclui teste de regressão para impedir o retorno do problema.

O texto final é independente do tema ou da decoração escolhida.
