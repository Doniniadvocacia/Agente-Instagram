from painel import build_index

ok = falhou = 0
def t(n,c):
    global ok,falhou
    if c: ok+=1; print("  ok  ",n)
    else: falhou+=1; print("  FALHA",n)

posts = [
 {"img":"posts/2026-07-24-tarde.png","editoria":"Direito do Consumidor","data":"24 jul 2026, 14h",
  "legenda":"O STJ decidiu nesta semana...\n\n#direito #consumidor #advocacia"},
 {"img":"posts/2026-07-24-manha.png","editoria":"Direito Civil","data":"24 jul 2026, 08h",
  "legenda":"Nova tese sobre responsabilidade...\n\n#direito #civil"},
]
h = build_index(posts, "24/07/2026 14:05")

t("HTML tem doctype", h.strip().startswith("<!DOCTYPE html>"))
t("mostra os dois posts", h.count('class="post"')==2)
t("tem botão copiar por post", h.count("Copiar legenda")==2)
t("tem link de download por post", h.count("download")>=2)
t("usa a cor do escritório", "#660b0a" in h)
t("legenda escapada (sem HTML cru)", "<script>alert" not in h)
t("mostra editoria e data", "Direito do Consumidor" in h and "24 jul 2026, 14h" in h)

# painel vazio
hv = build_index([], "24/07/2026")
t("painel vazio tem mensagem amigável", "Nenhum post gerado ainda" in hv)

# escapa conteúdo malicioso na legenda
hm = build_index([{"img":"p.png","editoria":"X","data":"d","legenda":"<script>alert(1)</script>"}])
t("injeção na legenda é neutralizada", "<script>alert(1)" not in hm and "&lt;script&gt;" in hm)

print(f"\n{ok} passaram, {falhou} falharam")
raise SystemExit(1 if falhou else 0)
