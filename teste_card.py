import os, tempfile
from PIL import Image
from gerar_card import gerar_card, _wrap, _font
from PIL import ImageDraw, Image as I

ok = falhou = 0
def t(nome, cond):
    global ok, falhou
    if cond: ok += 1; print("  ok  ", nome)
    else: falhou += 1; print("  FALHA", nome)

tmp = tempfile.mkdtemp()

# 1. Gera imagem no tamanho certo
out = os.path.join(tmp, "c1.png")
r = gerar_card("Notícias do Direito", "STJ fixa prazo para revisão de contratos bancários",
               "O que muda para as ações em curso", "@doniniadvocacia", "24 jul 2026", out)
t("arquivo gerado", os.path.exists(out))
im = Image.open(out)
t("dimensão 1080x1080", im.size == (1080, 1080))
t("modo RGB", im.mode == "RGB")

# 2. Manchete curta usa corpo grande
t("manchete curta em corpo grande (>=70px)", r["headline_px"] >= 70)

# 3. Manchete muito longa é reduzida e cabe em <=4 linhas
out2 = os.path.join(tmp, "c2.png")
longa = ("Tribunal Superior do Trabalho reconhece vínculo de emprego de motorista "
         "de aplicativo e define novos critérios para a caracterização da subordinação jurídica na economia digital")
r2 = gerar_card("Direito do Trabalho", longa, "", "@doniniadvocacia", "24 jul 2026", out2)
t("manchete longa cabe em <=4 linhas", r2["lines"] <= 4)
t("manchete longa reduziu o corpo", r2["headline_px"] < r["headline_px"])

# 4. Sem linha de apoio também funciona
t("gera sem apoio", os.path.exists(out2))

# 5. A logo foi de fato composta (canto inferior direito não é liso creme)
px = im.convert("RGB").load()
canto = [px[1008-40, 1008-30], px[1008-80, 1008-20], px[1008-160, 1008-40]]
t("logo presente no canto inferior direito", any(p != (230,228,220) for p in canto))

# 6. Faixa vermelha na lateral esquerda
t("faixa vermelha na lateral", px[10, 540] == (102, 11, 10))

# 7. Fundo creme no topo
t("fundo creme", px[600, 60] == (230, 228, 220))

# 8. Acentuação não quebra (usa caracteres PT-BR)
out3 = os.path.join(tmp, "c3.png")
gerar_card("Ação Civil", "Reparação por danos morais é ampliada em decisão inédita",
           "Índices de correção também mudam", "@doniniadvocacia", "24 jul 2026", out3)
t("acentuação PT-BR ok", os.path.exists(out3))

print(f"\n{ok} passaram, {falhou} falharam")
raise SystemExit(1 if falhou else 0)
