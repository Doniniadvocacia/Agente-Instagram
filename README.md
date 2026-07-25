# Agente de Instagram — Eduardo Donini Advocacia

Duas vezes por dia (8h e 14h), busca as principais notícias do direito, gera um
**card na identidade do escritório** e uma **legenda pronta**, e publica num
**painel de revisão**. Você abre o painel no celular, revisa, baixa a imagem,
copia a legenda e posta no Instagram.

**O agente não publica no Instagram.** Ele só prepara os rascunhos — a postagem
é sempre sua. (Publicação automática via API da Meta pode virar uma fase 2.)

---

## O que você recebe

Um painel na web (GitHub Pages) com os posts do dia. Cada um traz:
- a prévia do card 1080×1080, nas cores do escritório, com a logomarca
- botão **Copiar legenda**
- botão **Baixar imagem**

---

## Estrutura

```
agente-instagram.py     orquestrador (pesquisa → card → legenda → painel)
gerar_card.py           gera o card 1080x1080 (identidade visual)
painel.py               monta o HTML do painel
assets/logo.png         a logomarca (fundo transparente)
requirements.txt        dependência (pillow)
teste_card.py           testes do card
teste_painel.py         testes do painel
docs/                   o painel publicado (GitHub Pages serve daqui)
.github/workflows/agente-instagram.yml
```

---

## Instalação

### 1. Crie o repositório — **público**

Diferente do agente de artigos, este precisa ser **público**. O painel usa o
GitHub Pages, que só é gratuito em repositórios públicos. Não há segredo exposto:
a chave da API fica guardada como *secret* (criptografada, invisível mesmo em repo
público) e os cards/legendas são conteúdo que iria para o Instagram de qualquer forma.

> Se preferir manter privado, o GitHub Pages em repositório privado exige uma conta
> paga (GitHub Pro). Nesse caso, me avise que eu adapto para outra forma de entrega.

Suba todos os arquivos, **mantendo a estrutura de pastas** — em especial
`assets/logo.png`, `docs/` e `.github/workflows/`. Ao criar arquivos pelo navegador,
digite o caminho completo com barras (ex.: `assets/logo.png`) para o GitHub criar as
pastas. A logomarca já vai anexada, com o fundo removido.

### 2. Cadastre o único secret

Este agente usa **uma só credencial**. Em **Settings → Secrets and variables →
Actions → New repository secret**, crie:

| Secret | Onde obter |
|---|---|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com → API Keys |

(Não precisa de chave do Wix aqui — é outro serviço.)

### 3. Permissão de escrita

Em **Settings → Actions → General → Workflow permissions**, marque
**Read and write permissions** e salve. É o que deixa o agente publicar no painel.

### 4. Ligue o GitHub Pages

Em **Settings → Pages**:
- Em *Source*, escolha **Deploy from a branch**
- Branch: **main**, pasta: **/docs** — salve

Em um ou dois minutos, o GitHub mostra o endereço do painel, algo como
`https://SEU-USUARIO.github.io/agente-instagram/`. **Salve esse link no celular** —
é onde os posts vão aparecer.

### 5. Teste

Em **Actions → Agente de Instagram → Run workflow**, deixe `turno = auto` e marque
`mock = true`. Isso gera um post de exemplo (sem gastar a API), publica no painel e
te deixa ver o resultado. Abra o link do Pages e confira o card e os botões.

Quando quiser o primeiro post real, rode de novo com `mock` desmarcado.

Depois disso, ele roda sozinho às 8h e às 14h, todos os dias.

---

## Rodando na sua máquina

```bash
pip install pillow
export ANTHROPIC_API_KEY="..."

python3 agente-instagram.py --mock          # exemplo, sem API
python3 agente-instagram.py --turno=manha    # real
```

O painel fica em `docs/index.html` — abra no navegador.

---

## Ajustes

- **Cores** do card: constantes no topo de `gerar_card.py`
  (creme `#e6e4dc`, bege `#a68e6f`, vermelho `#660b0a`).
- **Fonte** da manchete: hoje é Liberation Serif. Para usar a fonte exata da marca,
  coloque o `.ttf` em `assets/` e ajuste `SERIF_BOLD` em `gerar_card.py`.
- **Editoria / tom / regras**: a constante `REGRAS` e o prompt em `agente-instagram.py`.
- **Horários**: os dois `cron` no início do workflow (estão em UTC; 11h e 17h UTC =
  8h e 14h de Brasília).

---

## As travas de conteúdo

Escritas no prompt (constante `REGRAS`): precisão factual (só o que veio das buscas),
texto original (sem copiar matérias), e conformidade com o Código de Ética e o
Provimento 205/2021 da OAB — sem promessa de resultado, sem captação, sem tom
mercantilista. E a trava maior: **nada é publicado sem a sua revisão.**

Leia cada legenda antes de postar, com atenção a nomes e números citados.

---

## Custos

- GitHub Actions: dentro da cota gratuita (execuções curtas).
- GitHub Pages: gratuito em repositório público.
- API da Anthropic: dois posts por dia, cada um com poucas buscas — custo baixo;
  acompanhe no console nas primeiras semanas.
