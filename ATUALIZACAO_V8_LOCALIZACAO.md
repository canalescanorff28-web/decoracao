# V8 — Localização inteligente + formulário guiado + WhatsApp Unicode robusto

## Localização
O formulário agora possui:
- botão `Usar GPS`;
- cidade;
- estado/UF;
- bairro;
- rua/avenida;
- número;
- complemento;
- CEP;
- ponto de referência;
- tipo/nome do local;
- latitude/longitude armazenadas quando GPS é autorizado.

O GPS usa `navigator.geolocation` do próprio navegador. Depois tenta uma consulta
de reverse geocoding ao OpenStreetMap/Nominatim para preencher o endereço. Se
essa consulta falhar, a cliente continua podendo preencher tudo manualmente.

## Campos guiados
- Tema com sugestões via `datalist`, sem impedir texto livre.
- Tipo/nome do local com sugestões, sem impedir texto livre.
- Quantidade de convidados com atalhos 30/50/80/100/150/300+.
- Itens para manter com chips selecionáveis.
- Itens para adaptar com chips selecionáveis.
- Textareas continuam disponíveis para detalhes livres.

## WhatsApp / emojis
O backend agora devolve também `whatsapp_message_encoded`, produzido com
`urllib.parse.quote`. Assim a mensagem chega ao JavaScript como ASCII percent-encoded:
- emojis → `%F0...`
- quebra de linha → `%0A`

O link `wa.me` usa essa versão pronta, evitando que Unicode seja corrompido por
alguma camada intermediária.

## Compatibilidade
`event_location` continua no banco como resumo do endereço para pedidos antigos
e para compatibilidade com clientes em cache.
