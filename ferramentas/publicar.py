"""Publica o dia no GitHub.

Uso: python3 ferramentas/publicar.py AAAA-MM-DD

- Repositório: boletins/AAAA-MM-DD/ com o PDF, boletim.json, noticias.json e whatsapp/ (capas + textos.md).
- Release com a tag AAAA-MM-DD: PDF, capas e os vídeos dos stories como anexos; textos do WhatsApp na descrição.
  Se a release não puder ser criada, os vídeos são gravados no próprio repositório (boletins/AAAA-MM-DD/stories/).
- README.md: índice com os links de cada dia (mais novo primeiro).
Imprime no final os links do dia.
"""
import json, os, subprocess, sys, glob

REPO = "ferretti641/boletim-42adm"
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
              "| Data | Boletim (PDF) | Stories e capas | Textos WhatsApp |", "|---|---|---|---|"]
    for d in dias:
        a, m, dd = d.split("-")
        base = f"https://github.com/{REPO}/blob/main/boletins/{d}"
        linhas.append(f"| {dd}/{m}/{a} | [PDF]({base}/boletim-42adm-{d}.pdf) | "
                      f"[release](https://github.com/{REPO}/releases/tag/{d}) | [textos]({base}/whatsapp/textos.md) |")
    linhas += ["", "_Conteúdo informativo. Não é recomendação de investimento nem parecer jurídico._", ""]
    open(os.path.join(RAIZ, "README.md"), "w", encoding="utf-8").write("\n".join(linhas))


# ---------- commit dos arquivos leves ----------
readme()
sh("git", "config", "user.name", "Rotina Boletim 42 ADM")
sh("git", "config", "user.email", "adm@42adm.com")
sh("git", "add", "README.md", "ferramentas", f"boletins/{dia}")
sh("git", "commit", "-m", f"Boletim Matinal {dia}", check=False)
sh("git", "push", "origin", "HEAD:main")

# ---------- release com os anexos ----------
textos = open(os.path.join(pasta, "whatsapp", "textos.md"), encoding="utf-8").read()
corpo = (f"**Boletim Matinal 42 ADM — {dia}**\n\n"
         f"📄 PDF: https://github.com/{REPO}/blob/main/boletins/{dia}/{pdf_nome}\n\n"
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
print("PDF:", f"{base}/{pdf_nome}")
print("Textos WhatsApp:", f"{base}/whatsapp/textos.md")
if rel.get("id") and not videos_falhos:
    print("Stories e capas (release):", f"https://github.com/{REPO}/releases/tag/{dia}")
else:
    print("Stories (no repositório):", f"https://github.com/{REPO}/tree/main/boletins/{dia}/stories")
if falhou:
    print("Anexos que falharam na release:", ", ".join(falhou))
