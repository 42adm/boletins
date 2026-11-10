"""Publica o dia no GitHub.

Uso: python3 ferramentas/publicar.py AAAA-MM-DD

- Repositório: boletins/AAAA-MM-DD/ com o PDF, boletim.json, noticias.json e whatsapp/ (capas + textos.md).
- Release com a tag AAAA-MM-DD: PDF, capas e os vídeos dos stories como anexos; textos do WhatsApp na descrição.
  Se a release não puder ser criada, os vídeos são gravados no próprio repositório (boletins/AAAA-MM-DD/stories/).
- README.md: índice com os links de cada dia (mais novo primeiro).
- icones/ e manifest.webmanifest: ícone azul do app (tela de início) e imagem de compartilhamento.
- index.html: página pública (GitHub Pages) com todos os boletins; cada dia abre em boletins/AAAA-MM-DD/ (HTML gerado pelo boletim.py).
Imprime no final os links do dia.
"""
import json, os, subprocess, sys, glob

REPO = "42adm/boletins"
# Endereço público (GitHub Pages) onde ficam todos os boletins
SITE = "https://42adm.github.io/boletins"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dia = sys.argv[1]
pasta = os.path.join(RAIZ, "boletins", dia)
pdf_nome = f"boletim-42adm-{dia}.pdf"
pdf = os.path.join(pasta, pdf_nome)
assert os.path.exists(pdf), f"PDF não encontrado: {pdf}"


def sh(*cmd, check=True, **kw):
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, **kw)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r


def gh_json(*args, input_path=None, check=True):
    cmd = ["gh", "api", *args]
    if input_path:
        cmd += ["--input", input_path]
    r = sh(*cmd, check=check)
    try:
        return json.loads(r.stdout) if r.stdout.strip() else {}
    except json.JSONDecodeError:
        return {"_raw": r.stdout, "_err": r.stderr}


# ---------- README (índice) ----------
def readme():
    dias = sorted((os.path.basename(p) for p in glob.glob(os.path.join(RAIZ, "boletins", "????-??-??"))), reverse=True)
    linhas = ["# Boletim Matinal 42 ADM", "",
              "Notícias e destaques do dia que impactam negócios, mercado e agronegócio, preparados pela "
              "[42 ADM](https://42adm.com) — BPO financeiro, consultoria e planejamento.", "",
              f"**Todos os boletins em: {SITE}**", "",
              "| Data | Boletim (página) | PDF | Stories e capas | Textos WhatsApp |", "|---|---|---|---|---|"]
    for d in dias:
        a, m, dd = d.split("-")
        base = f"https://github.com/{REPO}/blob/main/boletins/{d}"
        linhas.append(f"| {dd}/{m}/{a} | [abrir]({SITE}/boletins/{d}/) | [PDF]({base}/boletim-42adm-{d}.pdf) | "
                      + (f"[release](https://github.com/{REPO}/releases/tag/{d}) | [textos]({base}/whatsapp/textos.md) |"
                         if os.path.exists(os.path.join(RAIZ, "boletins", d, "whatsapp", "textos.md")) else "— | — |"))
    linhas += ["", "_Conteúdo informativo. Não é recomendação de investimento nem parecer jurídico._", ""]
    open(os.path.join(RAIZ, "README.md"), "w", encoding="utf-8").write("\n".join(linhas))


# ---------- página pública (GitHub Pages): index.html com todos os boletins ----------
def pagina():
    import html as H
    MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
             "setembro", "outubro", "novembro", "dezembro"]
    dias = sorted((os.path.basename(p) for p in glob.glob(os.path.join(RAIZ, "boletins", "????-??-??"))), reverse=True)
    cards, mes_atual = [], None
    for d in dias:
        a, m, dd = d.split("-")
        if not os.path.exists(os.path.join(RAIZ, "boletins", d, "index.html")):
            continue
        mes = f"{MESES[int(m) - 1].capitalize()} de {a}"
        if mes != mes_atual:
            cards.append(f'<h2 class="mes">{mes}</h2>')
            mes_atual = mes
        try:
            info = json.load(open(os.path.join(RAIZ, "boletins", d, "boletim.json"), encoding="utf-8"))
        except Exception:
            info = {}
        titulo = H.escape(info.get("data_extenso") or f"{dd}/{m}/{a}")
        temas = "".join(f"<li>{H.escape(s.get('titulo', ''))}</li>" for s in info.get("secoes", []))
        cards.append(
            f'<a class="card" href="boletins/{d}/">'
            f'<div class="data"><span class="dia">{dd}/{m}</span><span class="ext">{titulo}</span></div>'
            f'<ul>{temas}</ul><span class="abrir">Ler boletim →</span></a>')
    corpo = "\n".join(cards) or '<p class="vazio">Nenhum boletim publicado ainda.</p>'
    ultimo = next((f"boletins/{x}/" for x in dias if os.path.exists(os.path.join(RAIZ, "boletins", x, "index.html"))), "#")
    pagina_html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Boletim Matinal 42 ADM — todos os boletins</title>
<meta name="description" content="Notícias do dia que impactam negócios, mercado e agronegócio, preparadas pela 42 ADM.">
<meta property="og:title" content="Boletim Matinal 42 ADM — todos os boletins">
<meta property="og:description" content="Notícias do dia que impactam negócios, mercado e agronegócio, preparadas pela 42 ADM.">
<meta property="og:image" content="{SITE}/icones/og.png">
<meta property="og:url" content="{SITE}/">
<link rel="icon" type="image/png" href="icones/favicon-64.png">
<link rel="apple-touch-icon" href="icones/apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#1C3D7A">
<meta name="apple-mobile-web-app-title" content="Boletim 42">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#f4f6fa;color:#0b1c40;line-height:1.5}}
.topo{{position:sticky;top:0;z-index:10;background:#0b1c40;box-shadow:0 2px 10px rgba(0,0,0,.25)}}
.topo .in{{max-width:960px;margin:0 auto;padding:10px 16px;display:flex;align-items:center;justify-content:space-between;gap:12px}}
.topo img{{height:38px;display:block}}
.topo nav{{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}}
.topo nav a{{color:#fff;text-decoration:none;font-weight:600;font-size:.88rem;padding:7px 14px;border-radius:999px;border:1px solid rgba(255,255,255,.35);white-space:nowrap}}
.topo nav a.wa{{background:#99CA3C;color:#0b1c40;border-color:#99CA3C}}
@media (max-width:480px){{.topo img{{height:30px}} .topo nav a{{font-size:.8rem;padding:6px 10px}} .topo nav a.site{{display:none}}}}
header{{background:linear-gradient(135deg,#0b1c40,#1C3D7A);color:#fff;padding:36px 20px 48px;text-align:center}}
.contato{{max-width:760px;margin:0 auto 24px;padding:0 16px}}
.contato .box{{background:#0b1c40;color:#fff;border-radius:14px;padding:22px 20px;text-align:center}}
.contato h2{{font-size:1.15rem;margin-bottom:4px}}
.contato p{{opacity:.85;font-size:.92rem;margin-bottom:14px}}
.contato .links{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}}
.contato .links a{{color:#fff;text-decoration:none;font-size:.9rem;padding:8px 14px;border-radius:999px;background:rgba(255,255,255,.1)}}
.contato .links a.wa{{background:#99CA3C;color:#0b1c40;font-weight:700}}
header h1{{font-size:clamp(1.6rem,4vw,2.3rem);font-weight:800;letter-spacing:-.02em}}
header p{{opacity:.85;max-width:560px;margin:8px auto 22px}}
.btn{{display:inline-block;background:#99CA3C;color:#0b1c40;font-weight:700;padding:12px 22px;border-radius:999px;text-decoration:none}}
main{{max-width:760px;margin:-24px auto 40px;padding:0 16px}}
.mes{{font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;color:#5a6a8a;margin:28px 4px 10px}}
.card{{display:block;background:#fff;border-radius:14px;padding:18px 20px;margin-bottom:12px;text-decoration:none;color:inherit;
box-shadow:0 1px 3px rgba(11,28,64,.08);border-left:5px solid #99CA3C;transition:transform .15s,box-shadow .15s}}
.card:hover{{transform:translateY(-2px);box-shadow:0 6px 18px rgba(11,28,64,.12)}}
.data{{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}}
.dia{{font-size:1.4rem;font-weight:800;color:#1C3D7A}}
.ext{{color:#5a6a8a;font-size:.92rem}}
.card ul{{list-style:none;margin:8px 0 10px}}
.card li{{font-size:.95rem;padding:2px 0 2px 14px;position:relative}}
.card li:before{{content:"";position:absolute;left:0;top:.7em;width:6px;height:6px;border-radius:50%;background:#99CA3C}}
.abrir{{font-weight:700;color:#1C3D7A;font-size:.9rem}}
footer{{text-align:center;color:#5a6a8a;font-size:.82rem;padding:0 16px 40px}}
footer a{{color:#1C3D7A}}
</style></head><body>
<div class="topo"><div class="in">
<a href="{SITE}/"><img src="ferramentas/modelos/logo.png" alt="42 ADM"></a>
<nav><a class="site" href="https://42adm.com" target="_blank" rel="noopener">Nosso site</a>
<a class="wa" href="https://wa.me/5566981091019" target="_blank" rel="noopener">Comercial (66) 98109-1019</a></nav>
</div></div>
<header>
<h1>Boletim Matinal 42 ADM</h1>
<p>Notícias do dia que impactam negócios, mercado e agronegócio — todo dia cedo.</p>
<a class="btn" href="{ultimo}">Ler o boletim mais recente</a>
</header>
<main>
{corpo}
</main>
<section class="contato"><div class="box">
<h2>Fale com o comercial da 42 ADM</h2>
<p>BPO financeiro, consultoria, fluxo de caixa e planejamento para a sua empresa.</p>
<div class="links">
<a class="wa" href="https://wa.me/5566981091019" target="_blank" rel="noopener">WhatsApp (66) 98109-1019</a>
<a href="tel:+5566981091019">Ligar</a>
<a href="https://42adm.com" target="_blank" rel="noopener">42adm.com</a>
<a href="mailto:adm@42adm.com">adm@42adm.com</a>
<a href="https://instagram.com/42_adm" target="_blank" rel="noopener">Instagram @42_adm</a>
</div></div></section>
<footer>Preparado pela <a href="https://42adm.com">42 ADM</a> — BPO financeiro, consultoria e planejamento.<br>
Conteúdo informativo. Não é recomendação de investimento nem parecer jurídico.</footer>
</body></html>
"""
    open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8").write(pagina_html)
    open(os.path.join(RAIZ, ".nojekyll"), "w").close()
    # link fixo SITE/ultimo/ que sempre abre o boletim mais recente
    os.makedirs(os.path.join(RAIZ, "ultimo"), exist_ok=True)
    destino = "../" + ultimo if ultimo != "#" else "../"
    open(os.path.join(RAIZ, "ultimo", "index.html"), "w", encoding="utf-8").write(
        f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Boletim Matinal 42 ADM — último boletim</title>
<meta http-equiv="refresh" content="0; url={destino}">
<link rel="canonical" href="{SITE}/{ultimo if ultimo != '#' else ''}">
<script>location.replace("{destino}");</script>
</head><body><p>Abrindo o boletim mais recente… <a href="{destino}">clique aqui</a> se não abrir.</p></body></html>
""")


# ---------- commit dos arquivos leves ----------
readme()
pagina()
sh("git", "config", "user.name", "Rotina Boletim 42 ADM")
sh("git", "config", "user.email", "adm@42adm.com")
sh("git", "add", "README.md", "index.html", ".nojekyll", "ultimo", "ferramentas", f"boletins/{dia}")
sh("git", "commit", "-m", f"Boletim Matinal {dia}", check=False)
sh("git", "push", "origin", "HEAD:main")

# ---------- release com os anexos ----------
textos = open(os.path.join(pasta, "whatsapp", "textos.md"), encoding="utf-8").read()
corpo = (f"**Boletim Matinal 42 ADM — {dia}**\n\n"
         f"🌐 Boletim: {SITE}/boletins/{dia}/\n\n📄 PDF: https://github.com/{REPO}/blob/main/boletins/{dia}/{pdf_nome}\n\n"
         "Abaixo: os clipes dos stories (MP4) e as capas do WhatsApp (JPG) para baixar.\n\n" + textos)
if len(corpo) > 120000:
    corpo = corpo[:120000]
json.dump({"tag_name": dia, "name": f"Boletim Matinal {dia}", "body": corpo, "target_commitish": "main"},
          open("/tmp/release.json", "w", encoding="utf-8"), ensure_ascii=False)
rel = gh_json(f"repos/{REPO}/releases/tags/{dia}", check=False)
if not rel.get("id"):
    rel = gh_json("-X", "POST", f"repos/{REPO}/releases", input_path="/tmp/release.json", check=False)

anexos = [pdf] + sorted(glob.glob(os.path.join(pasta, "stories", "*.mp4"))) + \
    sorted(glob.glob(os.path.join(pasta, "whatsapp", "*.jpg")))
falhou = []
if rel.get("id"):
    ja = {a["name"] for a in rel.get("assets", [])}
    for f in anexos:
        nome = os.path.basename(f)
        if nome in ja:
            continue
        tipo = "application/pdf" if f.endswith(".pdf") else "video/mp4" if f.endswith(".mp4") else "image/jpeg"
        r = sh("gh", "api", "-X", "POST", "-H", f"Content-Type: {tipo}",
               f"https://uploads.github.com/repos/{REPO}/releases/{rel['id']}/assets?name={nome}",
               "--input", f, check=False)
        if r.returncode != 0:
            falhou.append(nome)
else:
    falhou = [os.path.basename(f) for f in anexos]
    print("Release não criada:", rel)

videos_falhos = [n for n in falhou if n.endswith(".mp4")]
if videos_falhos:
    # plano B: grava os vídeos no repositório
    sh("git", "add", "-f", f"boletins/{dia}/stories")
    sh("git", "commit", "-m", f"Stories {dia}", check=False)
    sh("git", "push", "origin", "HEAD:main")

base = f"https://github.com/{REPO}/blob/main/boletins/{dia}"
print("\nLINKS DO DIA")
print("Boletim (página):", f"{SITE}/boletins/{dia}/")
print("Todos os boletins:", SITE)
print("PDF:", f"{base}/{pdf_nome}")
print("Textos WhatsApp:", f"{base}/whatsapp/textos.md")
print("Último boletim (link fixo):", f"{SITE}/ultimo/")
if rel.get("id") and not videos_falhos:
    print("Stories e capas (release):", f"https://github.com/{REPO}/releases/tag/{dia}")
else:
    print("Stories (no repositório):", f"https://github.com/{REPO}/tree/main/boletins/{dia}/stories")
if falhou:
    print("Anexos que falharam na release:", ", ".join(falhou))
