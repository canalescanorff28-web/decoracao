# V8.6 — remove tremilique ao clicar

## Causas encontradas no vídeo
- o cabeçalho mudava de altura no estado `scrolled`;
- a logo mudava de 104px para 82px durante a rolagem;
- perto do topo, essa troca de dimensões causava deslocamento visual;
- abrir o drawer removia a barra de rolagem e podia deslocar o site lateralmente.

## Correções
- logo mantém tamanho constante no scroll;
- header mantém dimensões constantes;
- estado `scrolled` altera apenas fundo e sombra;
- detector de scroll ganhou histerese;
- `scrollbar-gutter: stable` reserva espaço da barra de rolagem;
- JS faz compensação adicional ao bloquear a página;
- clique na marca volta ao topo de forma controlada;
- removidos deslocamentos em estado `:active`;
- âncoras receberam margem adequada para o header;
- cache PWA atualizado.

## Resultado esperado
Ao clicar no logo, navegação, Minha inspiração, filtros e botões, a página não deve mais tremer ou deslocar alguns pixels.
