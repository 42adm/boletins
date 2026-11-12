# Rotina diária — Boletim Matinal 42 ADM

Instruções para a sessão programada que roda todo dia às 6h30 (horário de Brasília).
Escreva tudo em português do Brasil, linguagem simples, para donos de pequenas e médias empresas e produtores rurais
(a 42 ADM fica em Mato Grosso, região do Vale do Araguaia). Público: empresário que não é especialista em finanças.

**Foco fixo:** notícias e destaques do dia que impactam **negócios, mercado e agronegócio**. Nada de política partidária,
fofoca ou assunto sem efeito prático no caixa da empresa ou do produtor.

`DIA` = data de hoje no formato AAAA-MM-DD. Pasta do dia: `boletins/DIA/`.

## 1. Pesquisa (WebSearch, modo "extended"; WebFetch só em URLs vindas da busca)

Faça buscas separadas e em paralelo, sempre com a data de hoje ou de ontem no texto da busca. Confira que cada número
é do fechamento do último dia útil (ou da data indicada na fonte) — **nunca invente número**. Se não achar um dado,
deixe de fora ou escreva "a confirmar".

- **Economia:** Selic (e data da próxima reunião do Copom), dólar comercial (fechamento e variação do dia anterior),
  Ibovespa, inflação/IPCA e expectativa do Focus (o Focus sai às segundas), notícias de crédito e juros.
- **Impostos e regras:** reforma tributária (CBS/IBS), Simples Nacional, Receita Federal, prazos que afetem empresas.
- **Empresário:** varejo, consumo, inadimplência (Serasa), crédito para empresas, datas do comércio, folha/13º.
- **Campo:** soja, milho e boi — preços do dia em Paranaguá (porto), Sorriso, Rio Verde, Dourados, Luís Eduardo
  Magalhães e, sempre que houver, **Vale do Araguaia (Canarana, Barra do Garças, Vila Rica)**; boletim do Imea
  (plantio/colheita em MT), clima (El Niño, chuvas). Fontes: Cepea/Esalq, Imea, Notícias Agrícolas, Canal Rural,
  Scot Consultoria.
- Prefira fontes como Agência Brasil, Valor, InfoMoney, CNN Brasil, Metrópoles, g1, Folha, Estadão, Contábeis,
  Jornal Contábil, Serasa, Banco Central, Receita Federal.

Opcional: se no Gmail houver um e-mail de hoje com assunto "Boletim Matinal 42 ADM" (enviado por helio@42adm.com),
use-o só como conferência dos números — o boletim desta rotina é feito a partir da sua própria pesquisa.

Fim de semana: no sábado faça o resumo da semana; no domingo, um boletim mais leve com o que vem na semana
(agenda: Copom, Focus, IPCA, prazos). Use os fechamentos de sexta e diga isso no texto.

## 2. Boletim em página de internet + PDF (mesmo padrão do boletim do Helio)

Escreva `boletins/DIA/boletim.json` seguindo o formato descrito no topo de `ferramentas/boletim.py`
(veja o exemplo completo em `ferramentas/exemplo/boletim.json`). Estrutura:

1. Saudação de 1–2 frases (com o dia da semana) dizendo os assuntos do dia.
2. **Resumo rápido:** 3 a 5 tópicos, com os números principais em `<b>`.
3. Seções, nesta ordem quando houver assunto: **ECONOMIA** (4 cards: Selic, dólar, inflação esperada, próxima
   decisão/indicador do dia), **IMPOSTOS**, **EMPRESÁRIO** (1 ou 2 blocos), **CAMPO** (texto + tabela de preços por
   praça, com as praças do Vale do Araguaia em destaque). Cada seção termina com um "Na prática:" de 1–3 frases dizendo
   o que o empresário deve fazer. Na seção CAMPO use `"pratica_rotulo": "Para o produtor do Araguaia:"`.
4. **Prazos:** datas para anotar (Black Friday, 13º, Copom, impostos etc.).
5. **Dica financeira do dia:** uma conta simples e prática.
6. **Promo** da 42 ADM ligada ao assunto do dia (planejamento, fluxo de caixa, renegociação de dívidas, BPO).
7. **Chamada** de uma frase forte para o empresário.
8. Rodapé (aviso de conteúdo informativo + data dos dados) e **fontes** (título curto + URL real de cada fonte usada).

Gere o boletim: `python3 ferramentas/boletim.py boletins/DIA/boletim.json boletins/DIA/boletim-42adm-DIA.pdf`.
Isso cria `boletins/DIA/index.html` (o boletim como página de internet, com botão "Exportar PDF") e o PDF que o botão baixa.
Confira com `pdftoppm -r 70 -png` e Read: no máximo 2 páginas, nada cortado nem sobreposto. Se passar de 2 páginas,
encurte textos.

## 3. Notícias para stories e WhatsApp

Escolha de 4 a 6 notícias do boletim com mais impacto para empresários e produtores, mais a dica do dia (se a dica
for repetida de um dia anterior, pule). Escreva `boletins/DIA/noticias.json` no formato descrito no topo de
`ferramentas/midias.py` (exemplo em `ferramentas/exemplo/noticias.json`). Para cada notícia:

- `tag` (ECONOMIA, JUROS, DÓLAR, IMPOSTOS, VENDAS, COBRANÇA, ALERTA, CAMPO, DICA DO DIA…), `kicker` curto com a data
  ou fonte do dado, `headline` de manchete (até ~55 caracteres, 1–2 palavras-chave em `<em>`), 1 ou 2 `stats`,
  `note` curta, `takeLabel` + `take` com a ação prática.
- `whatsapp`: texto pronto, formatação do WhatsApp (`*negrito*`, `_itálico_`), assim:
  `*Manchete* emoji` / linha em branco / 2–3 frases com os números em negrito / linha em branco /
  `👉 *Na prática:* ...` / linha em branco / `_Boletim Matinal 42 ADM · DD/MM_`. Até 900 caracteres.
- Só use números que estão no boletim do dia.

O `midias.py` também coloca no topo do `whatsapp/textos.md` uma **mensagem do boletim completo**, montada a partir da saudação e do resumo do `boletim.json`, com o link do boletim do dia e o link fixo do último boletim publicado (https://42adm.github.io/boletins/ultimo/, que o `publicar.py` sempre aponta para o mais recente). Por isso o `boletim.json` precisa estar pronto antes de rodar o `midias.py`; o resumo deve funcionar bem também como texto de WhatsApp.

Confira primeiro as prévias: `python3 ferramentas/midias.py boletins/DIA/noticias.json boletins/DIA previa`
e abra `boletins/DIA/previa/folha.jpg` com Read. Corrija textos que estourem a área, que fiquem colados na borda
ou que se sobreponham (encurte a manchete, o label ou o valor). Depois gere tudo:
`python3 ferramentas/midias.py boletins/DIA/noticias.json boletins/DIA` e apague `boletins/DIA/previa`.

## 4. Publicar

`python3 ferramentas/publicar.py DIA` — grava tudo no repositório (página, PDF, capas, textos e os vídeos dos stories na pasta do dia) e atualiza o README e a página com todos os boletins (index.html).
Não existe mais release: não tente criar uma nem avise sobre isso. Se o push falhar por falta de permissão, não tente outro caminho: avise na mensagem final.

## 5. Enviar no canal do WhatsApp "42 ADM - Boletim Empresarial"

Só funciona quando a rotina roda com o computador do Juliano (ferramentas do Claude in Chrome disponíveis). Carregue a
skill `chrome-browser`, abra uma aba nova em https://web.whatsapp.com, vá em **Canais** e abra o canal
**42 ADM - Boletim Empresarial** (não envie em nenhuma outra conversa). Envie, nesta ordem:

1. A **mensagem do boletim completo** (o primeiro bloco do `whatsapp/textos.md`, com o link do boletim do dia).
2. Para cada notícia, na ordem do `noticias.json`: a capa `whatsapp/capa-<id>.jpg` com o texto `whatsapp` da notícia
   como legenda. Para anexar a capa, grave antes as capas em uma pasta do computador (ferramentas de arquivos do
   computador) e use o botão **+ → Fotos e vídeos** do WhatsApp Web. Se não der para anexar a imagem, envie só o texto.

Confira cada envio na tela antes do próximo e não repita mensagem já enviada. Se o WhatsApp Web pedir QR code, estiver
desconectado ou o Chrome não estiver disponível, não envie nada e diga isso em uma linha no aviso final.

## 6. Avisar o Juliano

Envie um SendUserMessage curto com: os 2–3 destaques do dia em uma linha cada, o link do boletim (página), o link do PDF, o link da pasta do dia
(stories e capas) e o link dos textos do WhatsApp (os três saem impressos pelo publicar.py). Lembre que a publicação
no Instagram é feita por ele. Diga se o envio no canal do WhatsApp (passo 5) deu certo.
