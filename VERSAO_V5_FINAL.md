# V5 — fechamento funcional e de experiência

Além do polimento visual da V4, esta versão fecha a experiência de solicitação:

## Drawer / solicitação em duas etapas
1. Cliente escolhe uma inspiração.
2. O site abre primeiro um resumo visual do que foi selecionado.
3. Cliente pode:
   - remover uma inspiração;
   - adicionar outra;
   - conferir total de referência.
4. Só depois toca em **Continuar personalização**.
5. O formulário completo aparece na segunda etapa.

## Sem inspiração selecionada
Ao abrir "Minha inspiração" com carrinho vazio:
- o formulário NÃO aparece;
- o site mostra uma tela simples orientando a escolher uma inspiração;
- há botão para voltar diretamente ao portfólio.

## Cache/PWA
- cache do service worker atualizado para `aline-erica-decor-v5`;
- `service-worker.js` passa a ser entregue com `no-cache/no-store`;
- reduz o risco de o navegador continuar exibindo versão antiga após deploy.

## Fluxo final
Inspiração → resumo → personalização → registro no Neon → WhatsApp gratuito via wa.me.
