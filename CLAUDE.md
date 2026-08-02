# Casamento — app do casamento do Diego & Débora

App **single-file** (`index.html`, ~890 linhas) da suíte pessoal. PWA instalável, dados na nuvem (Supabase), compartilhado entre Diego e Débora.

- **Live:** https://dkonrad88.github.io/casamento/ (GitHub Pages, publica sozinho no push da `main`)
- **Repo:** `dKonrad88/casamento` (aqui) — trabalhar sempre no `index.html`
- **Idioma:** PT-BR. Confirmar mudanças de visão com o Diego, mas **commit + push é autônomo**.

## Como rodar / verificar (workflow desta suíte)

O app precisa de login Supabase real → **não dá pra testar direto**. Fluxo usado:

1. Editar `index.html`.
2. **Validar sintaxe** com `jsc` (não tem node): extrair o `<script>` e `new Function(src)`. Caminho: `/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc`. Checar também chaves `{}` balanceadas no `<style>`.
3. **Preview:** montar uma cópia em `/private/tmp/.../scratchpad/demo/index.html` com um **shim de fake Supabase** (auto-login + `casamento_state` com dados de teste) — assim o app abre direto no home, sem login. Servir com um `server.py` mínimo que faz `os.chdir` antes (TCC bloqueia `os.getcwd()` em ~/Documents). `launch.json`: `autoPort:true`, porta via env `PORT` (não fixar). Abrir no Browser pane, `resize_window` mobile, screenshot.
4. **commit + push na `main`**. GitHub Pages publica. Tem `.nojekyll` (obrigatório na suíte).

> O scratchpad é limpo entre turnos — recriar `server.py`/demo quando sumir.

## Dados (Supabase)

- Projeto: **`jlouesrrmqeauzlgvrpw`** (nome "Habit Tracker"). URL/anon-key no topo do `index.html`.
- Tabela **`casamento_state (lista_id uuid, key text, value jsonb)`**, PK(lista_id,key), RLS por `is_membro(lista_id)`.
- Chaves (uma linha cada): **`convidados`, `tarefas`, `gastos`, `checklist`, `meta`, `data`**. Gravar SEMPRE via `CAS.set(key, valor)` — **não criar tabelas**.
- Helper global **`CAS`**: `CAS.get(key,def)` / `CAS.set(key,value)` (upsert na nuvem) / `CAS.espaco()` / `CAS.reload()`. `dados[key]` é atualizado sincronicamente no `set` antes do await → pode `CAS.get` logo depois e re-renderizar.
- 🛡️ **Fila de gravação (`cas_fila_v1` no localStorage)** — o `upsert` engolia o erro: quando a rede do celular falhava, a tela mostrava o dado novo, o banco não recebia nada e ninguém avisava (aconteceu de verdade em 02/08/2026, com duas edições perdidas). Agora `salvar()` grava na fila **antes** de tentar subir; só sai da fila quando o servidor confirma. Retry com backoff (3s→60s), reenvio no evento `online` e no `visibilitychange`, e `escoarFila()` roda no `boot()` **antes** do `carregarDados()`. O `carregarDados()` aplica as pendências **por cima** do que veio do servidor, senão a edição não-enviada sumiria da tela. Barra `.offbar` (`#filaBar`) abaixo do header mostra quantas estão pendentes.
- **Espaço do casal:** `listas` tipo=`casamento`, id **`74764948-e020-47cc-b176-ed38af0884eb`**. Membros: **Diego dono** (`7fec78a9-e0d4-4d7a-9a32-abdf16151593`, konraddiego@gmail.com) + **Débora membro** (`807fe468-627a-4e50-8969-3efec0cc4c7b`, debiandrade8@gmail.com). Data do casamento = **2027-10-16**.
- 🛡️ **GUARD:** trigger `protege_lista` (BEFORE DELETE em `public.listas`) bloqueia exclusão de listas tipo casamento/viagem (o espaço já sumiu 2x no passado por DELETEs misteriosos). Se sumir de novo, olhar `get_logs('api'/'postgres')` pela msg "PROTEGIDO".
- Fonte histórica dos dados = `hub_state` (blob JSON por user, `data->'casConvidados'` etc.) do módulo Casamento do HUB (`~/Documents/GitHub/hubpessoal`). Migração já foi feita; **NÃO re-migrar** (sobrescreve edições feitas no app).

## Design (Conceito 1 — Editorial, aprovado pelo Diego)

- **Fontes:** Playfair Display (títulos serifados), Cormorant Garamond (datas/labels), Inter (corpo).
- **Tema claro (padrão) = creme editorial**; tema escuro = "warm dark". Toggle no header. Vars em `:root` (dark) e `[data-theme="light"]`. Acento **dourado** (`--gold`). Azul/teal (`--primary`/`--primary2`) nos ícones/detalhes.
- **Moldura de celular** (`.phone`) no desktop/tela larga; tela cheia no celular/PWA (media query inverte). Modais/toast são `position:absolute` DENTRO do `.phone`.
- Sem paridade com o estilo do claude.ai — é identidade própria do app.

## Arquitetura do `index.html`

- IIFE única. **Router** por variável `view` (`home`/`inicio`/`convidados`/`tarefas`/`gastos`/`checklist`); `go(v)` troca. `render()` decide login / criar-espaço / home / seção.
- **Delegação de eventos no `document`** (NÃO no `#app`) — porque os modais/forms ficam fora do `#app`. `onAppClick` despacha por `data-act`. Também há listeners `input` (buscas, parcelas, filtro select) e `change` (select).
- **Forms** = bottom-sheet (`openForm(html)`/`closeForm()`), conteúdo em `#fBody`.
- **Header:** 3 ícones sem fundo — 🌙/☀️ tema · 🔄 atualizar · ⚙ config. Em `home` o header é transparente e o hero editorial fica no conteúdo.

## Telas

- **Home (`homeHTML`):** hero "Diego & Débora / Nosso casamento / data", fio dourado, **card de contagem** ("N dias para o grande dia" + coração azul-claro) — só informação, **não é clicável** —, faixa **`.figs.duo`** com Projeção × Meta (mesmo formato sóbrio da tela de Gastos; Meta vira "—" se não definida) e 4 tiles. O tile de Gastos mostra "R$ X a pagar" (projeção/meta já aparecem na faixa acima). A tela `inicio` continua existindo, mas **nada na home linka pra ela** — só a data quando não está definida (`setdata`).
- **Início (`renderInicio`):** resumo (contagem, confirmados, gasto vs meta via `gastosResumo()`, tarefas pendentes).
- **Convidados (`convListaHTML`/`renderConvidados`)** — a tela mais trabalhada:
  - Agrupado por nível (`NIVEIS`: Com certeza/Queremos/Pensar muito/Se couber). **Título do grupo** numa barra com fundo **marrom único** (`rgba(176,137,82,.18)`), **sem** bolinha.
  - **Casais:** nome do **homem primeiro** — reordenação só na exibição (`gGender`/`ordenaCasal`, heurística terminação -a/-o + listas `GEN_F`/`GEN_M`). "&" em azul. Nomes iguais (mesmo tom).
  - **Status pelo DOT** ao lado esquerdo: **neutro (cinza) até o convite ser enviado**; depois **verde=confirmado / laranja=pendente / vermelho=recusado** (`dotColor(c)` = `enviado ? statusColor(status) : cinza`).
  - **Ícones no fim do card, alinhados:** 👑 (padrinho, slot fixo) + **avião de papel** (`planeSVG`) = convite enviado (teal cheio) / não enviado (contorno). Tocar no avião alterna `enviado`. `.grow` expande (`.row .grow,.sw-content .grow`) pra empurrar os ícones sempre pro fim.
  - **Swipe (gestos, `sw*` funcs):** arrastar **→ direita** revela 3 botões (✓ confirmar / ⏳ pendente / ✕ recusar); **← esquerda** revela 🗑 excluir. Sem botões fixos. `SW_L=162, SW_R=-54`.
  - **Toolbar compacta:** `<select>` de filtro (Status / Convite enviado-não / Grupo) + 🔍 (abre busca) + ＋ (add). Resumo mostra "X de N convites enviados".
  - Status possíveis: **confirmado / pendente / recusado** (sem "talvez"). Todos os 109 estão `pendente` e `não enviado` agora (início limpo).
- **Gastos** — paridade funcional com o HUB + tratamento editorial (feito depois de Convidados):
  - **Topo editorial** (sem card): "PROJEÇÃO" em Cormorant maiúsculo espaçado + valor em Playfair, **Meta clicável** à direita (`data-act="gmeta"`, some o botão "Definir meta"), régua fina **dourada** (`.progl`, não o gradiente azul), fio `.rule` e faixa **`.figs`** com 4 números (Fechado/Pago/A pagar/Planejado) em Playfair, **sem cor e sem "R$"** (`fmtN`), separados por filete.
  - **Toolbar igual à de Convidados:** `<select>` (Fechados/Planejando/Todos) + 🔍 (toggle da busca) + ＋. Sem as pílulas `.seg` e sem o botão full-width.
  - **Lista:** barra `.grp` marrom com o nome do filtro + contagem. Cada linha é `.sw-content.gsw` — **cor só no dot** de 8px (`casStatusColor`), texto todo em tinta/cinza. Sub em **1 linha** com ellipsis; o **status textual só aparece em Planejando ou se cancelado** (em Fechados o dot já diz). Datas curtas dd/mm/aa (`fmtBRc`).
  - **Swipe** (sem botões fixos): **→ direita** = 💳 pagamentos (só em fechados), **← esquerda** = 🗑 excluir. Limites por linha via `data-swl`/`data-swr` (Gastos 54/-54, Convidados 162/-54).
  - **"O que falta pagar" (chevron)**: só em **fechados**, no fim da linha (`.parcbtn` + `chevSVG`). Toca e expande `gastoParcelasHTML(g)` — painel **read-only** com as parcelas em aberto (ordenadas por vencimento, data · label → valor) + "Falta N parcelas / total". Estado em `gasAberto{id:bool}`, **vários podem ficar abertos**; o toggle re-renderiza só `#gasList`. O painel é **irmão** do `.sw` (fora dele) — se ficasse dentro, deslizaria junto no swipe e esticaria os botões de ação. Tudo pago → "Tudo pago.".
    - Com **1 parcela em aberto e sem divergência**, o painel colapsa numa linha só ("Falta 1 parcela · data → valor"): listar a parcela E totalizar mostraria o mesmo número duas vezes, e isso lê como duas cobranças.
    - ⚠️ O "Falta pagar" vem de **`gasVal(g) − gPagoAmt(g)`**, NÃO da soma das parcelas em aberto: as parcelas lançadas podem não fechar com o valor do gasto. Quando divergem, o painel mostra o aviso `.warn`. Dados reais tinham 3 casos assim (Fotos R$ 50 a menos, Maquiagem R$ 250 a menos, Cabeleleira R$ 720 a mais).
  - **Valores:** em **fechado**, orçado riscado (só se ≠ do final) + final em Playfair + `▼ economia`; em **planejado**, o `valorIni` É o valor exibido com o rótulo "orçado" — nunca risca nem mostra "R$ 0,00".
  - `gastosResumo().economia` só conta **negociação real** (`vf>0 && vi>vf`) — antes somava o orçado inteiro dos planejados e inflava a economia.
  - **Campos de dinheiro:** classe `.money` → `maskMoney()` no listener de `input` aplica **máscara de centavos** (só dígitos, preenche da direita pra esquerda); `pm()` continua lendo o texto mascarado. Cobre `gVi`/`gVal` (editor de gasto, com wrapper `.minp` e "R$" fixo dentro do campo) e `.pv`/`gpEnt` (parcelas e entrada — **sem** o "R$" fixo, o campo de parcela é estreito demais e o cabeçalho já mostra o total). No listener, campo `.money` dentro de `#parcWrap` **precisa** chamar `gpCalc()` antes do `return`, senão a soma ao vivo para de atualizar.
  - Editor completo (desc/status/empresa/valorIni × valor final/obs) e **editor de pagamentos/parcelas** (`formPagamento`) inalterados. Gasto sem `tipo` conta como **fechado** (regra herdada do HUB).
- **Tarefas / Checklist:** funcionais (feito/pendente/quem/data; seções colapsáveis com itens). Ainda **não** ganharam o tratamento editorial completo — próximo passo natural.

## Gotchas

- `esc()` em tudo que vem de dados. IDs novos via `nid()`.
- Emojis não recebem `color` (são coloridos). Ícones de linha = SVG inline.
- Ao mexer em nomes/gênero: heurística nunca é 100% — nomes ambíguos ficam sem inverter.
- Data cleaning já rodado nos nomes (removidos parênteses, "- descritor", relação-só → palavra; alguns swaps homem-primeiro).

## Próximos passos (abertos)

- Levar o editorial pras abas **Tarefas** e **Checklist** (Convidados e Gastos já foram).
- Código morto de antes: `gEco()`, `gasPago()`, `gasCat()` não são usados por ninguém.
- Bug aberto em **Convidados**: o botão que chama `clinkPicker` ("Formar casal") não existe em lugar nenhum — o handler `clinkpick` e o picker estão prontos, mas inalcançáveis. E `persistConvidado` força `qtd = conj?2:1`, então não dá pra registrar família com filhos.
- Dashboard read-only no HUB (`hubpessoal`) apontando pra `casamento_state` (hoje o HUB lê o `hub_state` antigo e desatualiza).
