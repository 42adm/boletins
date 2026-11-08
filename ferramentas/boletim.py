"""Gera o PDF do Boletim Matinal 42 ADM a partir de um boletim.json.

Uso: python3 ferramentas/boletim.py boletins/AAAA-MM-DD/boletim.json boletins/AAAA-MM-DD/boletim.pdf

Formato do boletim.json (textos podem ter <b>negrito</b>; nada de outras tags):
{
  "data_extenso": "Sexta-feira, 6 de novembro de 2026",
  "saudacao": "Bom dia e boa sexta! ☀️ ...",
  "resumo": ["O Banco Central <b>manteve os juros em 13,75% ao ano</b> ...", "..."],
  "secoes": [
    {"tag": "ECONOMIA", "titulo": "Juros parados, dólar em alta",
     "cards": [{"rotulo": "Juros básicos (Selic)", "valor": "13,75%", "sub": "ao ano · mantidos em 4/11", "cor": "escuro|vermelho|verde|azul"}],
     "texto": "Parágrafo opcional...",
     "blocos": [{"titulo": "O que aconteceu", "texto": "..."}],
     "tabela": {"colunas": ["Região · praça", "", "Soja (R$/saca)", "Milho (R$/saca)", "Boi (R$/@)"],
                "linhas": [{"regiao": "REFERÊNCIA", "praca": "Paranaguá (porto) · boi SP", "valores": ["158,53", "69,00*", "390,85*"], "destaque": false}],
                "nota": "Saca de 60 kg; ... Fontes: ..."},
     "pratica_rotulo": "Na prática:", "pratica": "..."}
  ],
  "prazos": [{"data": "27/11", "texto": "Black Friday"}],
  "dica": "antes de dar desconto ...",
  "promo": {"titulo": "Planejamento 2027: ...", "texto": "..."},
  "chamada": "Empresário, venda boa é venda que vira dinheiro no caixa.",
  "rodape": "Conteúdo informativo. Não é recomendação de investimento nem parecer jurídico. ...",
  "fontes": [{"titulo": "Sou Brasília: Copom mantém a Selic", "url": "https://..."}]
}
Todas as chaves de "secoes" exceto tag e titulo são opcionais.
"""
import json, sys, os, html, base64
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(sys.argv[1], encoding="utf-8"))
saida = sys.argv[2]
logo = base64.b64encode(open(os.path.join(AQUI, "modelos", "logo.png"), "rb").read()).decode()


def t(s):
    """Escapa o texto mas mantém <b> e </b>."""
    s = html.escape(s or "", quote=False)
    return s.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")


COR = {"escuro": "#1f2937", "vermelho": "#b3261e", "verde": "#4d7c0f", "azul": "#1C3D7A"}


def secao(s):
    out = [f'<section><div class="sh"><span class="tag">{t(s["tag"])}</span><h2>{t(s["titulo"])}</h2></div>']
    if s.get("cards"):
        out.append('<div class="cards">' + "".join(
            f'<div class="card"><div class="cl">{t(c["rotulo"])}</div>'
            f'<div class="cv" style="color:{COR.get(c.get("cor", "escuro"), "#1f2937")}">{t(c["valor"])}</div>'
            f'<div class="cs">{t(c.get("sub", ""))}</div></div>' for c in s["cards"]) + "</div>")
    if s.get("texto"):
        out.append(f'<p class="tx">{t(s["texto"])}</p>')
    if s.get("blocos"):
        cls = "blocos dois" if len(s["blocos"]) > 1 else "blocos"
        out.append(f'<div class="{cls}">' + "".join(
            f'<div class="bloco"><h3>{t(b["titulo"])}</h3><p>{t(b["texto"])}</p></div>' for b in s["blocos"]) + "</div>")
    if s.get("tabela"):
        tb = s["tabela"]
        cols = tb["colunas"]
        head = "".join(f"<th>{t(c)}</th>" for c in cols)
        rows = ""
        for r in tb["linhas"]:
            cls = ' class="dest"' if r.get("destaque") else ""
            rows += (f'<tr{cls}><td class="rg">{t(r.get("regiao", ""))}</td><td>{t(r.get("praca", ""))}</td>'
                     + "".join(f'<td class="n">{t(v)}</td>' for v in r["valores"]) + "</tr>")
        out.append(f'<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>')
        if tb.get("nota"):
            out.append(f'<p class="nota">{t(tb["nota"])}</p>')
    if s.get("pratica"):
        out.append(f'<div class="pratica"><b class="pl">{t(s.get("pratica_rotulo", "Na prática:"))}</b> {t(s["pratica"])}</div>')
    out.append("</section>")
    return "".join(out)


SERVICOS = [("BPO Financeiro", "Cuidamos de todo o seu financeiro, com organização e relatórios claros."),
            ("Consultoria Financeira", "Diagnóstico e plano para cortar custos e aumentar o lucro."),
            ("Mentoria com Performance", "Acompanhamento de perto, com metas reais e método."),
            ("Renegociação de Dívidas", "Organizamos as dívidas para aliviar o caixa e voltar a crescer."),
            ("Fluxo de Caixa", "Controle do dinheiro que entra e sai, sem surpresas."),
            ("Planejamento Financeiro", "Metas e orçamento para o ano todo.")]
CONTATOS = [("WhatsApp", "(66) 98109-1019"), ("E-mail", "adm@42adm.com"), ("Instagram", "@42_adm"),
            ("LinkedIn", "42adm"), ("Facebook", "42 ADM"), ("YouTube", "@42adm22")]

corpo = "".join(secao(s) for s in d["secoes"])
prazos = ""
if d.get("prazos"):
    prazos = ('<section><div class="sh"><span class="tag">PRAZOS</span><h2>Datas para anotar</h2></div><div class="prazos">'
              + "".join(f'<span><b>{t(p["data"])}</b> {t(p["texto"])}</span>' for p in d["prazos"]) + "</div></section>")
dica = f'<div class="dica"><b>Dica financeira do dia:</b> {t(d["dica"])}</div>' if d.get("dica") else ""
promo = ""
if d.get("promo"):
    promo = (f'<div class="promo"><img src="data:image/png;base64,{logo}"><div><h3>{t(d["promo"]["titulo"])}</h3>'
             f'<p>{t(d["promo"]["texto"])}</p></div></div>')
fontes = ""
if d.get("fontes"):
    fontes = '<ol class="fontes">' + "".join(
        f'<li><a href="{html.escape(f["url"])}">{t(f["titulo"])}</a></li>' for f in d["fontes"]) + "</ol>"

doc = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 12mm 10mm 12mm 10mm; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Inter', sans-serif; color: #1f2937; font-size: 9.6pt; line-height: 1.38; }}
b {{ font-weight: 700; color: #111827; }}
.hero {{ background: #1C3D7A; color: #fff; border-radius: 12px; padding: 16px 20px 14px; border-bottom: 5px solid #99CA3C; position: relative; overflow: hidden; }}
.hero:after {{ content: ""; position: absolute; right: -60px; top: -40px; width: 260px; height: 260px; border-radius: 50%; border: 22px solid rgba(255,255,255,.06); }}
.hero .top {{ display: flex; justify-content: space-between; align-items: flex-start; }}
.hero img {{ height: 64px; }}
.hero .tt {{ text-align: right; }}
.hero h1 {{ font-size: 20pt; font-weight: 700; }}
.hero .dt {{ color: #99CA3C; font-size: 11pt; font-weight: 600; }}
.hero p {{ margin-top: 8px; font-size: 10.5pt; max-width: 88%; position: relative; z-index: 1; }}
.resumo {{ background: #eef1f8; border-left: 5px solid #1C3D7A; border-radius: 8px; padding: 10px 16px 10px 20px; margin-top: 10px; }}
.resumo h2 {{ color: #1C3D7A; font-size: 11pt; letter-spacing: .06em; margin-bottom: 4px; }}
.resumo li {{ margin-left: 16px; margin-bottom: 2px; }}
section {{ margin-top: 10px; break-inside: avoid; }}
.sh {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; break-after: avoid; }}
.tag {{ background: #99CA3C; color: #13234a; font-weight: 700; font-size: 8.5pt; letter-spacing: .1em; padding: 2px 9px; border-radius: 4px; }}
h2 {{ color: #1C3D7A; font-size: 12.5pt; font-weight: 700; }}
.cards {{ display: flex; gap: 8px; margin-bottom: 7px; break-inside: avoid; }}
.card {{ flex: 1; border: 1px solid #e3e6ee; border-top: 4px solid #1C3D7A; border-radius: 8px; padding: 6px 10px; }}
.cl {{ font-size: 8.6pt; color: #4b5563; }}
.cv {{ font-size: 14.5pt; font-weight: 700; }}
.cs {{ font-size: 8.6pt; color: #4b5563; }}
.tx {{ margin-bottom: 7px; }}
.blocos {{ display: flex; gap: 12px; margin-bottom: 7px; break-inside: avoid; }}
.bloco {{ flex: 1; border: 1px solid #e3e6ee; border-radius: 8px; padding: 9px 12px; }}
.bloco h3 {{ color: #2b4580; font-size: 10.5pt; margin-bottom: 4px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 9.2pt; break-inside: avoid; }}
th {{ background: #1C3D7A; color: #fff; text-align: left; padding: 4px 8px; font-weight: 600; }}
th:nth-child(n+3) {{ text-align: right; }}
td {{ padding: 3.5px 8px; border-bottom: 1px solid #e5e7eb; }}
td.rg {{ color: #6b7280; font-size: 8pt; letter-spacing: .08em; font-weight: 600; white-space: nowrap; }}
td.n {{ text-align: right; font-variant-numeric: tabular-nums; }}
tr.dest td {{ background: #f3f7e8; }}
.nota {{ font-size: 7.8pt; color: #6b7280; margin-top: 4px; }}
.pratica {{ background: #f3f7e8; border-left: 4px solid #99CA3C; border-radius: 6px; padding: 7px 14px; margin-top: 6px; break-inside: avoid; }}
.pratica .pl {{ color: #4d7c0f; }}
.prazos {{ border: 1px solid #e3e6ee; border-radius: 8px; padding: 7px 12px; display: flex; flex-wrap: wrap; gap: 4px 24px; }}
.prazos b {{ color: #1C3D7A; }}
.dica {{ border: 2px dashed #99CA3C; border-radius: 10px; padding: 9px 14px; margin-top: 12px; break-inside: avoid; }}
.dica > b:first-child {{ color: #1C3D7A; }}
.promo {{ background: #1C3D7A; color: #fff; border-radius: 12px; border-bottom: 5px solid #99CA3C; padding: 12px 18px; margin-top: 12px; display: flex; gap: 18px; align-items: center; break-inside: avoid; }}
.promo img {{ height: 52px; }}
.promo h3 {{ font-size: 12pt; }}
.promo b {{ color: #fff; }}
.cta {{ border: 2px solid #1C3D7A; border-radius: 12px; padding: 10px 16px; margin-top: 10px; text-align: center; break-inside: avoid; }}
.cta h3 {{ color: #1C3D7A; font-size: 14pt; }}
.cta > p {{ max-width: 80%; margin: 4px auto 10px; }}
.serv {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: left; }}
.serv div {{ background: #f3f7e8; border-radius: 8px; padding: 5px 9px; font-size: 8.2pt; }}
.serv h4 {{ color: #1C3D7A; font-size: 10pt; }}
.fale {{ margin-top: 10px; color: #4b5563; letter-spacing: .12em; font-weight: 700; font-size: 10pt; }}
.site {{ color: #1C3D7A; font-size: 17pt; font-weight: 700; }}
.ctt {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; margin-top: 6px; }}
.ctt span {{ background: #eef1f8; border-radius: 999px; padding: 3px 12px; font-size: 9pt; }}
.rod {{ font-size: 7.8pt; color: #6b7280; margin-top: 10px; border-top: 1px solid #e5e7eb; padding-top: 6px; }}
.fontes {{ columns: 3; font-size: 7.6pt; color: #4b5563; margin: 4px 0 0 14px; }}
.fontes a {{ color: #4b5563; }}
</style></head><body>
<div class="hero"><div class="top"><img src="data:image/png;base64,{logo}"><div class="tt"><h1>Boletim Matinal</h1><div class="dt">{t(d["data_extenso"])}</div></div></div>
<p>{t(d.get("saudacao", ""))}</p></div>
<div class="resumo"><h2>RESUMO RÁPIDO</h2><ul>{"".join(f"<li>{t(r)}</li>" for r in d.get("resumo", []))}</ul></div>
{corpo}{prazos}{dica}{promo}
<div class="cta"><h3>{t(d.get("chamada", "Empresário, seu financeiro em dia é mais lucro no caixa."))}</h3>
<p>Enquanto você cuida de vender e produzir, a <b>42 ADM</b> cuida do financeiro: contas a pagar e receber, cobrança, conciliação bancária, fluxo de caixa e planejamento. Mais tempo para você, mais lucro para a empresa.</p>
<div class="serv">{"".join(f"<div><h4>{a}</h4>{b}</div>" for a, b in SERVICOS)}</div>
<div class="fale">FALE COM A GENTE</div><div class="site">42adm.com</div>
<div class="ctt">{"".join(f"<span>{a} <b>{b}</b></span>" for a, b in CONTATOS)}</div>
<p style="margin-top:6px;color:#4b5563;font-size:9pt">Chame no WhatsApp ou responda esta mensagem para falar com a nossa equipe.</p></div>
<div class="rod">{t(d.get("rodape", "Conteúdo informativo. Não é recomendação de investimento nem parecer jurídico."))}</div>
{fontes}
</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.set_content(doc, wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.pdf(path=saida, format="A4", print_background=True, prefer_css_page_size=True)
    b.close()
print("ok", saida)
