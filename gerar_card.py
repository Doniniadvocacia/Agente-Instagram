"""
Gerador de card de Instagram — Eduardo Donini Advocacia.
Recebe editoria, manchete e linha de apoio; devolve um PNG 1080x1080
na identidade visual do escritório, com a logomarca no rodapé.
Módulo puro: nenhuma chamada de rede, para poder ser testado isolado.
"""
import os
from PIL import Image, ImageDraw, ImageFont

# Paleta do LAYOUT DO ESCRITÓRIO (não confundir com a do sistema de gestão)
CREME       = (230, 228, 220)   # #e6e4dc
BEGE        = (166, 142, 111)   # #a68e6f
VERMELHO    = (102, 11, 10)     # #660b0a
BEGE_ESCURO = (138, 111, 82)

BASE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get("FONT_DIR", "/usr/share/fonts/truetype/liberation/")
LOGO_PATH = os.path.join(BASE, "assets", "logo.png")

def _font(name, size, fallback="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"):
    for path in (os.path.join(FONT_DIR, name), name):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.truetype(fallback, size)

SERIF_BOLD = "LiberationSerif-Bold.ttf"
SERIF_IT   = "LiberationSerif-Italic.ttf"
SANS       = "LiberationSans-Regular.ttf"
SANS_BOLD  = "LiberationSans-Bold.ttf"

def _tracked(draw, xy, text, fnt, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking

def _wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def gerar_card(editoria, manchete, apoio, handle, data, out_path):
    S, LEFT, RIGHT = 1080, 110, 1008
    img = Image.new("RGB", (S, S), CREME)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, 22, S], fill=VERMELHO)                       # faixa lateral

    # nome do escritório no topo, com filete
    _tracked(d, (LEFT, 150), "EDUARDO DONINI ADVOCACIA", _font(SANS, 34), VERMELHO, 6)
    d.line([LEFT, 214, 610, 214], fill=BEGE, width=2)

    # editoria
    d.rectangle([LEFT, 322, LEFT + 16, 338], fill=VERMELHO)
    _tracked(d, (LEFT + 34, 318), editoria.upper(), _font(SANS_BOLD, 26), BEGE, 3)

    # manchete: reduz o corpo até caber em no máximo 4 linhas
    size = 78
    while size >= 46:
        fnt = _font(SERIF_BOLD, size)
        lines = _wrap(d, manchete, fnt, RIGHT - LEFT)
        if len(lines) <= 4:
            break
        size -= 4
    # rede de segurança: manchete ainda longa é truncada com reticências
    if len(lines) > 4:
        lines = lines[:4]
        ult = lines[3]
        while ult and d.textlength(ult + "…", font=fnt) > (RIGHT - LEFT):
            ult = ult[:-1].rstrip()
        lines[3] = ult + "…"
    y = 430
    for ln in lines:
        d.text((LEFT, y), ln, font=fnt, fill=VERMELHO)
        y += int(size * 1.14)

    if apoio:
        y += 14
        fit = _font(SERIF_IT, 34)
        for ln in _wrap(d, apoio, fit, RIGHT - LEFT):
            d.text((LEFT, y), ln, font=fit, fill=BEGE_ESCURO)
            y += int(34 * 1.2)

    # divisor + rodapé: apenas o perfil
    d.line([LEFT, 895, RIGHT, 895], fill=BEGE, width=2)
    d.text((LEFT, 935), handle, font=_font(SANS_BOLD, 30), fill=VERMELHO)

    img.save(out_path)
    return {"path": out_path, "headline_px": size, "lines": len(lines)}

if __name__ == "__main__":
    import sys, json
    # Uso: gerar_card.py <editoria> <manchete> <apoio> <handle> <data> <saida>
    a = sys.argv[1:]
    print(json.dumps(gerar_card(*a), ensure_ascii=False))
