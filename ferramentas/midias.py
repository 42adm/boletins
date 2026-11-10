"""Gera os clipes dos stories (MP4 1080x1920, 13 s), as capas do WhatsApp (JPG 1080x1350)
e o arquivo whatsapp.md a partir de um noticias.json.

Uso:
  python3 ferramentas/midias.py boletins/AAAA-MM-DD/noticias.json boletins/AAAA-MM-DD/ previa   # só quadros de conferência
  python3 ferramentas/midias.py boletins/AAAA-MM-DD/noticias.json boletins/AAAA-MM-DD/          # tudo

Formato do noticias.json:
{
  "date": "06 · 11 · 2026",
  "data_curta": "06/11",
  "noticias": [
    {"id": "01-juros-dolar", "tag": "ECONOMIA", "kicker": "Fechamento de quinta · 5/11",
     "headline": "Juros parados e <em>dólar em alta</em>",
     "stats": [{"value": 13.75, "decimals": 2, "suffix": "%", "label": "Selic mantida"},
               {"text": "9/12", "label": "próxima decisão"}],
     "note": "Frase curta com um dado de apoio",
     "takeLabel": "NA PRÁTICA", "take": "O que o empresário deve fazer (até ~110 caracteres).",
     "whatsapp": "*Título em negrito* emoji\\n\\nTexto...\\n\\n👉 *Na prática:* ...\\n\\n_Boletim Matinal 42 ADM · 06/11_"}
  ]
}
Regras de tamanho: headline até ~55 caracteres; no máximo 2 stats; com 2 stats, valores curtos
(até 6 caracteres cada, ex.: "13,75%", "5,48", "R$ 30"); note até ~45 caracteres.
"""
import json, os, sys, subprocess
from concurrent.futures import ProcessPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(AQUI, "modelos")
DUR, FPS = 13.0, 30


SITE = "https://42adm.github.io/boletins"


def mensagem_boletim(pasta, d):
    """Texto pronto para o WhatsApp com o resumo do dia, o link do boletim completo e o link fixo
    do último boletim publicado (SITE/ultimo/, criado pelo publicar.py). Usa o boletim.json da pasta."""
    import re
    dia = os.path.basename(os.path.normpath(pasta))
    arq = os.path.join(pasta, "boletim.json")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", dia) or not os.path.exists(arq):
        return ""
    b = json.load(open(arq, encoding="utf-8"))

    def wa(t):
        t = re.sub(r"</?(b|strong)>", "*", t)
        t = re.sub(r"</?(em|i)>", "_", t)
        return re.sub(r"<[^>]+>", "", t).replace("&nbsp;", " ").strip()

    curta = d.get("data_curta") or f"{dia[8:]}/{dia[5:7]}"
    linhas = [f"*Boletim Matinal 42 ADM · {curta}*", ""]
    if b.get("saudacao"):
        linhas += [wa(b["saudacao"]), ""]
    linhas += [f"• {wa(r)}" for r in b.get("resumo", [])]
    linhas += ["", f"📄 *Boletim completo de hoje:* {SITE}/boletins/{dia}/",
               f"🔗 *Último boletim publicado (link fixo):* {SITE}/ultimo/",
               "", "_Conteúdo informativo. Não é recomendação de investimento._"]
    return "\n".join(linhas)


def _clipe(args):
    n, date, pasta, previa = args
    from playwright.sync_api import sync_playwright
    c = dict(n, date=date)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto("file://" + os.path.join(MOD, "clipe.html"))
        pg.evaluate("document.fonts.ready")
        pg.evaluate("([c,d]) => setup(c,d)", [c, DUR])
        if previa:
            pg.evaluate("seek(10)")
            pg.screenshot(path=os.path.join(pasta, "previa", f"story-{n['id']}.jpg"), type="jpeg", quality=80)
        else:
            final = os.path.join(pasta, "stories", f"story-{n['id']}.mp4")
            tmp = final[:-4] + ".part.mp4"
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-c:v", "mjpeg",
                                   "-framerate", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                                   "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp],
                                  stdin=subprocess.PIPE)
            for f in range(int(DUR * FPS)):
                pg.evaluate(f"seek({f / FPS})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            ff.stdin.close()
            if ff.wait() == 0:
                os.rename(tmp, final)
        # capa do WhatsApp
        pg2 = b.new_page(viewport={"width": 1080, "height": 1350})
        pg2.goto("file://" + os.path.join(MOD, "capa.html"))
        pg2.evaluate("document.fonts.ready")
        pg2.evaluate("c => setup(c)", c)
        sub = "previa" if previa else "whatsapp"
        pg2.screenshot(path=os.path.join(pasta, sub, f"capa-{n['id']}.jpg"), type="jpeg", quality=92)
        b.close()
    return n["id"]


if __name__ == "__main__":
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    pasta = sys.argv[2]
    previa = len(sys.argv) > 3 and sys.argv[3] == "previa"
    for sub in (["previa"] if previa else ["stories", "whatsapp"]):
        os.makedirs(os.path.join(pasta, sub), exist_ok=True)
    jobs = [(n, d["date"], pasta, previa) for n in d["noticias"]]
    with ProcessPoolExecutor(max_workers=3) as ex:
        for i in ex.map(_clipe, jobs):
            print("ok", i)
    if previa:
        # folha de contato: story à esquerda, capa à direita, uma linha por notícia
        from PIL import Image
        linhas = []
        for n in d["noticias"]:
            s = Image.open(os.path.join(pasta, "previa", f"story-{n['id']}.jpg")).resize((405, 720))
            c = Image.open(os.path.join(pasta, "previa", f"capa-{n['id']}.jpg")).resize((576, 720))
            linhas.append((s, c))
        cols = 3
        rows = (len(linhas) + cols - 1) // cols
        folha = Image.new("RGB", (cols * 1001, rows * 730), "white")
        for k, (s, c) in enumerate(linhas):
            x, y = (k % cols) * 1001, (k // cols) * 730
            folha.paste(s, (x, y)); folha.paste(c, (x + 415, y))
        folha.save(os.path.join(pasta, "previa", "folha.jpg"), quality=80)
        print("folha:", os.path.join(pasta, "previa", "folha.jpg"))
    else:
        with open(os.path.join(pasta, "whatsapp", "textos.md"), "w", encoding="utf-8") as f:
            f.write(f"# Textos para WhatsApp — {d.get('data_curta', d['date'])}\n\n")
            msg = mensagem_boletim(pasta, d)
            if msg:
                f.write("## Mensagem do boletim completo (sem imagem)\n\n"
                        "Cole no WhatsApp como mensagem de texto, antes ou depois das capas.\n\n"
                        f"```\n{msg}\n```\n\n")
            f.write("Envie cada capa com o texto correspondente na legenda.\n\n")
            for n in d["noticias"]:
                f.write(f"## capa-{n['id']}.jpg\n\n```\n{n['whatsapp']}\n```\n\n")
        print("textos:", os.path.join(pasta, "whatsapp", "textos.md"))
