#!/usr/bin/env python3
"""
AGENTE DE INSTAGRAM — Eduardo Donini Advocacia

A cada execução:
  1. PESQUISA  — busca as principais notícias do direito (em geral) do dia
  2. SELEÇÃO   — escolhe a de maior interesse para um post
  3. CARD      — gera a imagem 1080x1080 na identidade do escritório
  4. LEGENDA   — redige a legenda (regras da OAB embutidas)
  5. PAINEL    — publica no painel de revisão (GitHub Pages)

Nunca publica no Instagram. Entrega rascunhos para revisão e postagem manual.

Uso:
  python3 agente-instagram.py                 # turno pela hora
  python3 agente-instagram.py --turno=manha
  python3 agente-instagram.py --mock          # sem chamar a API (teste)
"""
import os, sys, json, datetime, urllib.request
from gerar_card import gerar_card
from painel import build_index

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODELO = "claude-sonnet-5"
HANDLE = "@doniniadvocacia"

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")
POSTS_DIR = os.path.join(DOCS, "posts")
MANIFEST = os.path.join(DOCS, "posts.json")
MAX_POSTS = 40

MESES = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]

REGRAS = """
REGRAS INEGOCIÁVEIS para a legenda (conteúdo de escritório de advocacia):
1. PRECISÃO: só afirme fatos, números e nomes que viu nos resultados de busca. Nada de memória.
2. ORIGINALIDADE: não copie trechos das matérias; escreva com palavras próprias.
3. OAB (Código de Ética e Provimento 205/2021): conteúdo informativo e sóbrio.
   PROIBIDO: prometer resultado, captar clientela, tom mercantilista/sensacionalista,
   chamadas comerciais ("entre em contato", "contrate", "agende"), emojis em excesso.
4. Tom impessoal, sem primeira pessoa do singular.
"""

def log(*a):
    print(f"[{datetime.datetime.now().isoformat(timespec='seconds')}]", *a)

def turno_atual():
    h = datetime.datetime.now().hour
    return "manha" if h < 12 else "tarde"

def claude(system, prompt, buscas=8, max_tokens=6000):
    body = {
        "model": MODELO, "max_tokens": max_tokens, "system": system,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": buscas,
                   "user_location": {"type": "approximate", "city": "Caxias do Sul",
                                     "region": "Rio Grande do Sul", "country": "BR",
                                     "timezone": "America/Sao_Paulo"}}]
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read())
    texto = "\n".join(b["text"] for b in data.get("content", []) if b.get("type") == "text").strip()
    return texto

def extrair_json(texto):
    t = texto.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    i, f = t.find("{"), t.rfind("}")
    if i == -1 or f == -1:
        raise ValueError("Resposta sem JSON:\n" + texto[:800])
    return json.loads(t[i:f+1])

def pesquisar(evitar):
    log("Pesquisando as notícias do direito do dia...")
    hoje = datetime.datetime.now().strftime("%d/%m/%Y")
    system = f"""Você é editor de conteúdo jurídico de um escritório de advocacia brasileiro.
Acompanha o noticiário do direito EM GERAL (não só uma área): STF, STJ, tribunais,
novas leis, decisões relevantes, temas de consumidor, trabalho, civil, penal, tributário,
família, empresarial. Seleciona o que é mais interessante e compartilhável para o público leigo
e profissional no Instagram.
{REGRAS}
Responda SOMENTE com JSON válido, sem preâmbulo e sem cercas de código."""

    ja_feitos = "\n".join(f"- {t}" for t in evitar) if evitar else "(nenhum)"
    prompt = f"""Hoje é {hoje}. Pesquise na web as principais notícias jurídicas do dia no Brasil
e escolha UMA para virar um post de Instagram — a mais relevante e de maior apelo.

NÃO repita nenhum destes temas já postados recentemente:
{ja_feitos}

Retorne exatamente esta estrutura JSON:
{{
  "editoria": "área do direito, curta (ex.: Direito do Consumidor)",
  "manchete": "título curto e forte para o card, no máximo 9 palavras, sem ponto final",
  "apoio": "uma linha de apoio curta, no máximo 8 palavras",
  "legenda": "legenda do Instagram: 3 a 5 frases explicando a notícia de forma clara e informativa, terminando com uma linha em branco e 4 a 6 hashtags relevantes em português",
  "fontes": ["url1", "url2"],
  "checagem": "uma frase confirmando que os dados vieram das buscas"
}}"""
    post = extrair_json(claude(system, prompt))
    log(f"  Tema: {post['editoria']} — {post['manchete']}")
    return post

def post_mock():
    return {
        "editoria": "Direito do Consumidor",
        "manchete": "STJ amplia direito de arrependimento em compras online",
        "apoio": "Prazo passa a contar da efetiva entrega",
        "legenda": ("O STJ firmou entendimento que amplia o direito de arrependimento nas compras "
                    "feitas pela internet. Segundo a decisão, o prazo de sete dias passa a ser contado "
                    "a partir da efetiva entrega do produto, e não da data da compra. A mudança reforça "
                    "a proteção do consumidor em contratações a distância.\n\n"
                    "#direito #consumidor #comprasonline #stj #advocacia"),
        "fontes": ["https://exemplo.gov.br/noticia"],
        "checagem": "post fictício de teste"
    }

def carregar_manifest():
    if os.path.exists(MANIFEST):
        try:
            return json.load(open(MANIFEST, encoding="utf-8"))
        except Exception:
            return []
    return []

def main():
    args = sys.argv[1:]
    mock = "--mock" in args
    dry = "--dry-run" in args
    turno = next((a.split("=")[1] for a in args if a.startswith("--turno=")), turno_atual())
    turno_lbl = {"manha": "manhã", "tarde": "tarde"}.get(turno, turno)

    if not mock and not ANTHROPIC_API_KEY:
        log("ERRO: falta a variável ANTHROPIC_API_KEY."); sys.exit(1)

    os.makedirs(POSTS_DIR, exist_ok=True)
    manifest = carregar_manifest()
    evitar = [p["manchete"] for p in manifest[:12]]

    post = post_mock() if mock else pesquisar(evitar)

    agora = datetime.datetime.now()
    data_lbl = f"{agora.day} {MESES[agora.month-1]} {agora.year}, {turno_lbl}"
    ts = agora.strftime("%Y-%m-%d") + "-" + turno
    img_rel = f"posts/{ts}.png"
    img_abs = os.path.join(DOCS, img_rel)

    log("Gerando o card...")
    info = gerar_card(post["editoria"], post["manchete"], post.get("apoio", ""),
                      HANDLE, data_lbl, img_abs)
    log(f"  Card em {info['headline_px']}px, {info['lines']} linhas.")

    if dry:
        log("--dry-run: card gerado, painel NÃO atualizado.")
        log(json.dumps(post, ensure_ascii=False, indent=2)); return

    registro = {"ts": ts, "img": img_rel, "editoria": post["editoria"],
                "manchete": post["manchete"], "data": data_lbl, "legenda": post["legenda"]}
    manifest = [registro] + [p for p in manifest if p.get("ts") != ts]
    manifest = manifest[:MAX_POSTS]
    json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    html = build_index(manifest, agora.strftime("%d/%m/%Y %H:%M"))
    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(html)

    log("Painel atualizado.")
    log(f"  Post: {post['editoria']} — {post['manchete']}")
    log(f"  Total de posts no painel: {len(manifest)}")

if __name__ == "__main__":
    main()

