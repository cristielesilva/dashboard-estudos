"""
Dashboard do escritório CSA ADVOCACIA
Rodar (dentro da pasta escritorio):  streamlit run app.py

- Intimações: buscadas no Diário de Justiça Eletrônico Nacional (DJEN/CNJ) pelo número da sua OAB
  (e das OABs dos parceiros). O app busca sozinho uma vez por dia ao abrir; o capturar.py faz o mesmo
  agendado no Windows, mesmo com o app fechado.
- Tudo fica em dados/escritorio.json (só no seu computador, fora do GitHub).
"""
import calendar
import datetime as dt
import hashlib
import hmac
import html
import re
import time

import pandas as pd
import streamlit as st

import nucleo as nc

st.set_page_config(page_title="CSA Advocacia · Painel", page_icon="⚖️", layout="wide")

# Tema claro. No Streamlit Cloud vale o config.toml da raiz (tema escuro do dashboard de estudos),
# então o app aplica o próprio tema e recarrega uma vez.
TEMA = {"base": "light", "primaryColor": "#1F6FEB", "backgroundColor": "#F4F6FA",
        "secondaryBackgroundColor": "#FFFFFF", "textColor": "#1F2937"}
if any(st.get_option(f"theme.{k}") != v for k, v in TEMA.items()) and not st.session_state.get("_tema_ok"):
    st.session_state._tema_ok = True
    try:
        for k, v in TEMA.items():
            st._config.set_option(f"theme.{k}", v)
        st.rerun()
    except Exception:
        pass

AZUL, MARINHO, FUNDO, TEXTO, APAGADO, BORDA = "#1F6FEB", "#0B2545", "#F4F6FA", "#1F2937", "#6B7280", "#E5E7EB"
VERMELHO, LARANJA, VERDE = "#DC2626", "#F59E0B", "#16A34A"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, p, label {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: {FUNDO}; color: {TEXTO}; }}
h1, h2, h3, h4 {{ color: #111827 !important; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2rem; max-width: 1350px; }}
[class*="st-key-card_"] {{ background: #fff; border: 1px solid {BORDA} !important; border-radius: 14px;
  box-shadow: 0 4px 14px rgba(15,23,42,.05); padding: 16px 18px !important; }}
.kpi {{ background: #fff; border: 1px solid {BORDA}; border-radius: 14px; padding: 18px; display: flex; gap: 16px;
  align-items: center; box-shadow: 0 4px 14px rgba(15,23,42,.05); height: 100%; }}
.kpi .ic {{ min-width: 54px; height: 54px; border-radius: 12px; display: flex; align-items: center;
  justify-content: center; font-size: 1.5rem; }}
.kpi .rot {{ color: {APAGADO}; font-size: .82rem; }}
.kpi .val {{ color: #111827; font-size: 1.8rem; font-weight: 700; line-height: 1.25; }}
.kpi .det {{ font-size: .8rem; color: {APAGADO}; }}
.kpi .det b {{ color: {AZUL}; font-weight: 600; }}
.cab {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px; }}
.cab h4 {{ margin: 0 !important; font-size: 1.05rem !important; font-weight: 600 !important; padding: 0 !important; }}
.cab span {{ color: {APAGADO}; font-size: .8rem; }}
.item {{ display: flex; gap: 12px; align-items: flex-start; padding: 9px 0; border-bottom: 1px solid #F1F3F6; }}
.item:last-child {{ border-bottom: none; }}
.item .dot {{ width: 9px; height: 9px; border-radius: 50%; margin-top: 7px; flex: none; }}
.item .tit {{ font-weight: 600; font-size: .9rem; color: #111827; }}
.item .sub {{ font-size: .78rem; color: {APAGADO}; }}
.item .quando {{ margin-left: auto; font-size: .8rem; font-weight: 600; white-space: nowrap; }}
.chip {{ display: inline-block; border-radius: 999px; padding: 2px 10px; font-size: .74rem; font-weight: 600;
  margin-right: 6px; background: #EEF4FF; color: {AZUL}; }}
.chip.verm {{ background: #FEE2E2; color: {VERMELHO}; }}
.chip.lar {{ background: #FEF3C7; color: #B45309; }}
.chip.verde {{ background: #DCFCE7; color: {VERDE}; }}
.chip.cinza {{ background: #F3F4F6; color: {APAGADO}; }}
.cal {{ width: 100%; border-collapse: collapse; text-align: center; font-size: .85rem; }}
.cal th {{ color: {APAGADO}; font-weight: 500; padding: 4px 0; }}
.cal td {{ padding: 5px 0; }}
.cal td span {{ display: inline-flex; width: 30px; height: 30px; align-items: center; justify-content: center;
  border-radius: 50%; position: relative; }}
.cal td.fora span {{ color: #C7CBD3; }}
.cal td.hoje span {{ background: {AZUL}; color: #fff; font-weight: 700; }}
.cal td.evento span::after {{ content: ""; position: absolute; bottom: 1px; width: 5px; height: 5px;
  border-radius: 50%; background: {VERMELHO}; }}
.cal td.hoje.evento span::after {{ background: #fff; }}
.calg {{ table-layout: fixed; }}
.calg td {{ vertical-align: top; height: 92px; border: 1px solid #EEF0F4; text-align: left; padding: 4px 6px; width: 14.28%; }}
.calg td .n {{ font-size: .8rem; color: {APAGADO}; font-weight: 600; }}
.calg td.hoje {{ background: #EEF4FF; }}
.calg td.hoje .n {{ color: {AZUL}; }}
.calg .ev {{ font-size: .7rem; border-radius: 6px; padding: 1px 5px; margin-top: 3px; background: #FEE2E2; color: #991B1B;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.calg .ev.aud {{ background: #E0E7FF; color: #3730A3; }}
.calg .ev.ok {{ background: #DCFCE7; color: #166534; text-decoration: line-through; }}
.texto-intim {{ background: #F9FAFB; border: 1px solid {BORDA}; border-radius: 10px; padding: 12px 14px; font-size: .86rem;
  white-space: pre-wrap; max-height: 360px; overflow-y: auto; color: {TEXTO}; }}
.ola {{ font-size: 1.45rem; font-weight: 700; color: #111827; }}
.ola-sub {{ color: {APAGADO}; font-size: .9rem; }}
.pill-esc {{ display: inline-flex; gap: 10px; align-items: center; background: #fff; border: 1px solid {BORDA};
  border-radius: 999px; padding: 5px 6px 5px 16px; font-weight: 600; font-size: .85rem; color: #111827; }}
.pill-esc .av {{ width: 32px; height: 32px; border-radius: 50%; background: {AZUL}; color: #fff; display: flex;
  align-items: center; justify-content: center; font-weight: 700; }}
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{ border-radius: 10px; }}
[data-testid="stSidebar"] {{ background: {MARINHO}; }}
[data-testid="stSidebar"] * {{ color: #E5ECF6; }}
[data-testid="stSidebar"] .stButton > button {{ border: none; background: transparent; color: #E5ECF6;
  justify-content: flex-start; padding-left: 14px; }}
[data-testid="stSidebar"] .stButton > button * {{ justify-content: flex-start; text-align: left; }}
[data-testid="stSidebar"] .stButton > button:hover {{ background: #13345E; color: #fff; }}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{ background: {AZUL}; color: #fff; }}
.st-key-btn_buscar button {{ border: 1px solid #2B4C7E !important; background: #13345E !important; justify-content: center !important; }}
.st-key-btn_buscar button * {{ justify-content: center !important; }}
.logo {{ font-size: 1.45rem; font-weight: 700; color: #fff !important; letter-spacing: .5px; }}
.logo span {{ color: #7FB0FF !important; }}
.logo-sub {{ font-size: .72rem; color: #9FB3CF !important; letter-spacing: 1.4px; text-transform: uppercase; }}
.st-key-acoes button {{ height: 46px; background: #fff; border: 1px solid {BORDA}; justify-content: flex-start; }}
.st-key-acoes button:hover {{ border-color: {AZUL}; color: {AZUL}; }}
</style>
""", unsafe_allow_html=True)

PAGINAS = [("painel", "🏠", "Painel"), ("intimacoes", "🔔", "Intimações"), ("processos", "📁", "Processos"),
           ("clientes", "👥", "Clientes"), ("prospeccao", "🎯", "Prospecção"), ("parceiros", "🤝", "Parceiros"),
           ("prazos", "⏰", "Prazos"), ("agenda", "📅", "Agenda"), ("tarefas", "☑️", "Tarefas"),
           ("peticoes", "📝", "Petições"), ("config", "⚙️", "Configurações")]
DIAS_SEMANA = ["D", "S", "T", "Q", "Q", "S", "S"]
MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro",
         "Novembro", "Dezembro"]
HOJE = dt.date.today()

# ───────────────────────── Senha e cópia online ─────────────────────────
def ler_segredos():
    try:
        return {k: (dict(v) if hasattr(v, "keys") else v) for k, v in st.secrets.items()}
    except Exception:
        return nc.segredos_locais()


SEGREDOS = ler_segredos()
SENHA = str(SEGREDOS.get("senha") or "")
if SENHA and not st.session_state.get("_entrou"):
    st.markdown("<div style='height:12vh'></div>", unsafe_allow_html=True)
    _, meio, _ = st.columns([1, 1.2, 1])
    with meio, st.container(border=True, key="card_login"):
        st.markdown("<div class='ola'>⚖️ CSA ADVOCACIA</div><div class='ola-sub'>Painel do escritório</div>",
                    unsafe_allow_html=True)
        with st.form("login"):
            tentativa = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", type="primary", width="stretch"):
                if hmac.compare_digest(tentativa.encode(), SENHA.encode()):
                    st.session_state._entrou = True
                    st.rerun()
                st.error("Senha incorreta.")
    st.stop()


@st.cache_resource(show_spinner=False)
def ligar_nuvem(_segredos, chave):
    return nc.ativar_nuvem(_segredos), nc.NUVEM


ERRO_NUVEM, nc.NUVEM = ligar_nuvem(SEGREDOS, hashlib.sha256(
    nc.limpar_token((SEGREDOS.get("github") or {}).get("token")).encode()).hexdigest())
if nc.NUVEM and time.time() - st.session_state.get("_ultimo_pull", 0) > 20:
    st.session_state._ultimo_pull = time.time()
    nc.NUVEM.puxar()

banco = nc.ler_dados()
cfg = banco["config"]
st.session_state.setdefault("pagina", "painel")


# ───────────────────────── Ajudantes ─────────────────────────
def salvar(msg=None, icone="✅"):
    erro = nc.gravar_dados(banco)
    if erro:
        st.session_state.aviso = (erro, "⚠️")
    elif msg:
        st.session_state.aviso = (msg, icone)


def ir(pagina, **extra):
    st.session_state.pagina = pagina
    st.session_state.update(extra)


def esc(t):
    return html.escape(str(t or ""))


def cabecalho(titulo, detalhe=""):
    st.markdown(f"<div class='cab'><h4>{titulo}</h4><span>{detalhe}</span></div>", unsafe_allow_html=True)


def kpi(icone, cor_fundo, rotulo, valor, detalhe):
    st.markdown(f"<div class='kpi'><div class='ic' style='background:{cor_fundo}'>{icone}</div><div>"
                f"<div class='rot'>{rotulo}</div><div class='val'>{valor}</div><div class='det'>{detalhe}</div>"
                f"</div></div>", unsafe_allow_html=True)


def extras():
    return cfg.get("feriados_extras", []), bool(cfg.get("feriados_moveis"))


def dias_para(venc):
    return (nc.para_data(venc) - HOJE).days


def rotulo_prazo(venc):
    d = dias_para(venc)
    if d < 0:
        return f"Vencido há {-d}d", VERMELHO, "verm"
    if d == 0:
        return "Hoje", VERMELHO, "verm"
    if d == 1:
        return "Amanhã", LARANJA, "lar"
    if d <= 5:
        return nc.br(venc)[:5], LARANJA, "lar"
    return nc.br(venc)[:5], AZUL, ""


def prazos_abertos():
    return sorted([p for p in banco["prazos"] if p.get("status") != "Cumprido"], key=lambda p: p["vencimento"])


def nome_proc(num):
    p = banco["processos"].get(num) or {}
    return p.get("numero_fmt") or nc.mascara_cnj(num)


def cliente_proc(num):
    p = banco["processos"].get(num) or {}
    return p.get("cliente") or ", ".join(x["nome"] for x in p.get("partes", [])[:2]) or ""


def intimacoes_ordenadas(filtro=None):
    lista = sorted(banco["intimacoes"].values(), key=lambda i: (i.get("data", ""), i.get("capturada_em", "")), reverse=True)
    return [i for i in lista if filtro is None or filtro(i)]


def novo_prazo(processo, descricao, vencimento, inicio=None, origem=None, peca=None, tipo="Prazo", hora=""):
    p = {"id": nc.novo_id(), "processo": processo, "descricao": descricao, "vencimento": nc.para_data(vencimento).isoformat(),
         "inicio": nc.para_data(inicio).isoformat() if inicio else None, "origem": origem, "peca": peca,
         "tipo": tipo, "hora": hora, "status": "Aberto", "criado": HOJE.isoformat()}
    banco["prazos"].append(p)
    return p


def criar_rascunho(intim, proc_num, modelo_nome, peca=None):
    modelos = nc.ler_modelos(banco)
    modelo = modelos.get(modelo_nome) or modelos.get("Manifestação simples") or {"texto": ""}
    campos = nc.campos_do_processo(banco, intim=intim, proc=banco["processos"].get(proc_num))
    r = {"id": nc.novo_id(), "titulo": f"{peca or modelo_nome} · {campos['processo']}", "processo": proc_num,
         "intimacao": (intim or {}).get("id"), "modelo": modelo_nome, "peca": peca or modelo_nome,
         "texto": nc.preencher(modelo["texto"], campos), "criado": dt.datetime.now().isoformat(timespec="minutes"),
         "status": "Rascunho"}
    banco["rascunhos"].insert(0, r)
    return r


def capturar_agora(dias=None):
    if not cfg.get("oabs") and not cfg.get("parceiros"):
        st.session_state.aviso = ("Cadastre o número da sua OAB em ⚙️ Configurações para buscar as intimações.", "⚠️")
        return
    with st.spinner("Buscando intimações no Diário de Justiça Eletrônico Nacional..."):
        novas, erros = nc.capturar(banco, dias=dias)
    erro = nc.gravar_dados(banco)
    if erro:
        erros.append(erro)
    if erros:
        st.session_state.aviso = (" · ".join(erros), "⚠️")
    else:
        st.session_state.aviso = (f"{novas} intimação(ões) nova(s) encontrada(s)." if novas
                                  else "Nenhuma intimação nova. Está tudo em dia.", "🔔")


# Busca automática uma vez por dia (quando o app abre)
ultima = nc.para_data(banco.get("ultima_busca"))
if (cfg.get("oabs") or cfg.get("parceiros")) and (ultima is None or ultima < HOJE) \
        and not st.session_state.get("_auto_busca"):
    st.session_state._auto_busca = True
    capturar_agora()

# ───────────────────────── Menu lateral ─────────────────────────
nao_lidas = sum(1 for i in banco["intimacoes"].values() if not i.get("lida"))
urgentes = sum(1 for p in prazos_abertos() if dias_para(p["vencimento"]) <= 2)
with st.sidebar:
    st.markdown(f"<div class='logo'>⚖️ CSA <span>ADVOCACIA</span></div><div class='logo-sub'>Painel do escritório</div>",
                unsafe_allow_html=True)
    st.write("")
    for chave, icone, nome in PAGINAS:
        extra = f"  ({nao_lidas})" if chave == "intimacoes" and nao_lidas else (
            f"  ({urgentes} urgentes)" if chave == "prazos" and urgentes else "")
        st.button(f"{icone}  {nome}{extra}", key=f"nav_{chave}", width="stretch",
                  type="primary" if st.session_state.pagina == chave else "secondary", on_click=ir, args=(chave,))
    st.write("")
    st.button("🔄  Buscar intimações agora", key="btn_buscar", width="stretch", on_click=capturar_agora)
    ub = banco.get("ultima_busca")
    st.caption(f"Última busca: {nc.br(ub)} {ub[11:16] if ub else 'nunca'}" if ub else "Última busca: nunca")
    if nc.NUVEM:
        st.caption("☁️ Cópia online ligada" + (f" · ⚠️ {nc.NUVEM.ultimo_erro}" if nc.NUVEM.ultimo_erro else " · sincronizada"))
    elif ERRO_NUVEM:
        st.caption(f"☁️ Cópia online desligada: {ERRO_NUVEM}")

if "aviso" in st.session_state:
    msg, icone = st.session_state.pop("aviso")
    st.toast(msg, icon=icone)


def topo():
    h = dt.datetime.now().hour
    saud = "Bom dia" if h < 12 else ("Boa tarde" if h < 18 else "Boa noite")
    nome = (cfg.get("advogada") or "").split(" ")[0]
    c1, c2 = st.columns([3, 2], vertical_alignment="center")
    c1.markdown(f"<div class='ola'>{saud}, {esc(nome)}</div><div class='ola-sub'>{HOJE.day} de "
                f"{MESES[HOJE.month - 1].lower()} de {HOJE.year}</div>", unsafe_allow_html=True)
    c2.markdown(f"<div style='display:flex;justify-content:flex-end'><div class='pill-esc'>{esc(cfg.get('escritorio'))}"
                f"<div class='av'>{esc((cfg.get('escritorio') or 'C')[0])}</div></div></div>", unsafe_allow_html=True)
    st.write("")


# ═════════════ Painel ═════════════
def mini_calendario(ano, mes, marcados):
    cal = calendar.Calendar(firstweekday=6)
    linhas = ""
    for semana in cal.monthdatescalendar(ano, mes):
        tds = ""
        for d in semana:
            cls = []
            if d.month != mes:
                cls.append("fora")
            if d == HOJE:
                cls.append("hoje")
            if d in marcados:
                cls.append("evento")
            tds += f"<td class='{' '.join(cls)}'><span>{d.day}</span></td>"
        linhas += f"<tr>{tds}</tr>"
    cab = "".join(f"<th>{d}</th>" for d in DIAS_SEMANA)
    return f"<table class='cal'><tr>{cab}</tr>{linhas}</table>"


def pagina_painel():
    topo()
    if not cfg.get("oabs"):
        st.info("**Primeiro passo:** cadastre o número da sua OAB em ⚙️ Configurações. A partir daí o painel busca "
                "sozinho, todo dia, as intimações publicadas no Diário de Justiça Eletrônico Nacional.", icon="👋")
    procs = [p for p in banco["processos"].values() if p.get("status") != "Arquivado"]
    patrona = sum(1 for p in procs if p.get("tipo") == "Patrona")
    abertos = prazos_abertos()
    hoje_n = sum(1 for p in abertos if dias_para(p["vencimento"]) <= 0)
    semana_n = sum(1 for p in abertos if 0 <= dias_para(p["vencimento"]) <= 7)
    novas_semana = sum(1 for i in banco["intimacoes"].values()
                       if nc.para_data(i.get("data")) and (HOJE - nc.para_data(i["data"])).days <= 7)
    tarefas = [t for t in banco["tarefas"] if not t.get("feita")]
    k = st.columns(4)
    with k[0]:
        kpi("📁", "#EEF4FF", "Processos ativos", len(procs), f"<b>{patrona}</b> meu patrocínio · <b>{len(procs) - patrona}</b> parcerias")
    with k[1]:
        kpi("⏰", "#FEF3C7", "Prazos em aberto", len(abertos), f"<b>{hoje_n}</b> hoje/vencidos · <b>{semana_n}</b> em 7 dias")
    with k[2]:
        kpi("🔔", "#FEE2E2", "Intimações não lidas", nao_lidas, f"<b>{novas_semana}</b> publicadas nos últimos 7 dias")
    with k[3]:
        kpi("☑️", "#DCFCE7", "Tarefas pendentes", len(tarefas), f"<b>{len(banco['rascunhos'])}</b> rascunhos de petição")
    st.write("")

    c1, c2, c3 = st.columns([1.35, 1.25, 1])
    with c1, st.container(border=True, key="card_intim"):
        cabecalho("🔔 Intimações recentes", f"{nao_lidas} não lidas")
        lista = intimacoes_ordenadas()[:6]
        if not lista:
            st.caption("Nenhuma intimação ainda. Elas aparecem aqui depois da primeira busca.")
        for i in lista:
            a = nc.analisar(i)
            cor = AZUL if not i.get("lida") else "#C7CBD3"
            st.markdown(f"<div class='item'><div class='dot' style='background:{cor}'></div><div>"
                        f"<div class='tit'>{esc(a['peca'])} · {esc(i.get('tipo') or i.get('documento'))}</div>"
                        f"<div class='sub'>{esc(i['processo_fmt'])} · {esc(i['tribunal'])} · {esc(cliente_proc(i['processo']))}</div>"
                        f"</div><div class='quando' style='color:{APAGADO}'>{nc.br(i['data'])[:5]}</div></div>",
                        unsafe_allow_html=True)
        st.button("Ver todas as intimações →", key="ver_intim", on_click=ir, args=("intimacoes",))
    with c2, st.container(border=True, key="card_prazos"):
        cabecalho("⏰ Prazos próximos", f"{len(abertos)} em aberto")
        if not abertos:
            st.caption("Sem prazos em aberto. Crie um prazo a partir de uma intimação.")
        for p in abertos[:6]:
            rot, cor, _ = rotulo_prazo(p["vencimento"])
            st.markdown(f"<div class='item'><div class='dot' style='background:{cor}'></div><div>"
                        f"<div class='tit'>{esc(p['descricao'])}</div>"
                        f"<div class='sub'>{esc(nome_proc(p['processo']))} · {esc(cliente_proc(p['processo']))}</div>"
                        f"</div><div class='quando' style='color:{cor}'>{rot}{(' ' + p['hora']) if p.get('hora') else ''}</div></div>",
                        unsafe_allow_html=True)
        st.button("Ver todos os prazos →", key="ver_prazos", on_click=ir, args=("prazos",))
    with c3, st.container(border=True, key="card_cal"):
        cabecalho(f"📅 {MESES[HOJE.month - 1]} {HOJE.year}")
        marcados = {nc.para_data(p["vencimento"]) for p in abertos}
        st.markdown(mini_calendario(HOJE.year, HOJE.month, marcados), unsafe_allow_html=True)
        hoje_ev = [p for p in abertos if nc.para_data(p["vencimento"]) == HOJE]
        st.caption(f"🔴 {len(hoje_ev)} compromisso(s) hoje")

    c1, c2, c3 = st.columns([1.35, 1.25, 1])
    with c1, st.container(border=True, key="card_procs"):
        cabecalho("📁 Processos movimentados", "pela última intimação")
        recentes = sorted(procs, key=lambda p: p.get("ultima_mov") or "", reverse=True)[:5]
        if not recentes:
            st.caption("Os processos são criados sozinhos a partir das intimações, ou em 📁 Processos.")
        for p in recentes:
            chip = "<span class='chip'>Patrona</span>" if p.get("tipo") == "Patrona" else \
                f"<span class='chip lar'>Parceria{(' · ' + esc(p.get('parceiro'))) if p.get('parceiro') else ''}</span>"
            st.markdown(f"<div class='item'><div><div class='tit'>{esc(cliente_proc(p['numero']) or 'Cliente não informado')} {chip}</div>"
                        f"<div class='sub'>{esc(p.get('numero_fmt'))} · {esc(p.get('ultima_mov_resumo', ''))[:110]}</div></div>"
                        f"<div class='quando' style='color:{APAGADO}'>{nc.br(p.get('ultima_mov'))[:5]}</div></div>",
                        unsafe_allow_html=True)
    with c2, st.container(border=True, key="card_tarefas"):
        cabecalho("☑️ Tarefas pendentes", f"{len(tarefas)}")
        if not tarefas:
            st.caption("Nada pendente.")
        for t in sorted(tarefas, key=lambda t: t.get("data") or "9999")[:6]:
            if st.checkbox(f"{t['titulo']}" + (f" · {nc.br(t['data'])[:5]}" if t.get("data") else ""), key=f"pt_{t['id']}"):
                t["feita"] = True
                salvar("Tarefa concluída.")
                st.rerun()
    with c3, st.container(border=True, key="card_acoes"):
        cabecalho("⚡ Ações rápidas")
        with st.container(key="acoes"):
            a1, a2 = st.columns(2)
            st.button("🔔  Ver intimações", width="stretch", on_click=ir, args=("intimacoes",))
            st.button("⏰  Novo prazo ou audiência", width="stretch", on_click=ir, args=("prazos",))
            st.button("📝  Nova petição", width="stretch", on_click=ir, args=("peticoes",))
            st.button("👥  Novo cliente", width="stretch", on_click=ir, args=("clientes",), kwargs={"aba_clientes": "novo"})
            st.button("🎯  Prospecção", width="stretch", on_click=ir, args=("prospeccao",))


# ═════════════ Intimações ═════════════
def formulario_prazo(i, a, chave):
    ext, mov = extras()
    proc = i["processo"]
    if a["peca"] == "Audiência designada":
        data = st.date_input("Data da audiência", value=nc.para_data((a.get("audiencia") or {}).get("data")) or HOJE,
                             format="DD/MM/YYYY", key=f"aud_d_{chave}")
        hora = st.text_input("Hora", value=(a.get("audiencia") or {}).get("hora", ""), key=f"aud_h_{chave}")
        if st.button("Salvar na agenda", key=f"aud_ok_{chave}", type="primary"):
            novo_prazo(proc, f"Audiência · {nome_proc(proc)}", data, origem=i["id"], tipo="Audiência", hora=hora)
            i["lida"] = True
            salvar("Audiência salva na agenda.")
            st.rerun()
        return
    peca = st.text_input("Peça / providência", value=a["peca"], key=f"pz_p_{chave}")
    c1, c2 = st.columns(2)
    dias = c1.number_input("Prazo (dias)", 1, 120, int(a["dias"] or 5), key=f"pz_d_{chave}")
    uteis = c2.toggle("Dias úteis", value=True, key=f"pz_u_{chave}")
    pub, ini, venc = nc.calcular_prazo(i["data"], int(dias), uteis, ext, mov)
    st.caption(f"Disponibilizada {nc.br(i['data'])} → publicada {nc.br(pub)} → começa {nc.br(ini)}")
    venc = st.date_input("Vencimento (confira)", value=venc, format="DD/MM/YYYY", key=f"pz_v_{chave}")
    if st.button("Salvar prazo", key=f"pz_ok_{chave}", type="primary"):
        novo_prazo(proc, peca, venc, ini, i["id"], peca)
        i["lida"] = True
        i["prazo_criado"] = True
        salvar(f"Prazo salvo: {peca} até {nc.br(venc)}.")
        st.rerun()


def cartao_intimacao(i, chave):
    a = nc.analisar(i)
    proc = banco["processos"].get(i["processo"]) or {}
    origem = "<span class='chip'>Meu patrocínio</span>" if i.get("origem") == "patrona" else \
        f"<span class='chip lar'>Parceria · {esc(i.get('origem'))}</span>"
    lida = "<span class='chip cinza'>Lida</span>" if i.get("lida") else "<span class='chip verm'>Nova</span>"
    prazo_txt = f"{a['dias']} dias{' (CLT)' if a['trabalhista'] else ''}" if a["dias"] else "agendar"
    with st.container(border=True, key=f"card_i_{chave}"):
        st.markdown(f"{lida}{origem}<span class='chip verde'>Sugestão: {esc(a['peca'])} · {prazo_txt}</span>"
                    f"{'<span class=chip>Prazo criado</span>' if i.get('prazo_criado') else ''}", unsafe_allow_html=True)
        st.markdown(f"**{esc(i['processo_fmt'])}** · {esc(i['tribunal'])} · {esc(i['orgao'])}  \n"
                    f"<span style='color:{APAGADO};font-size:.85rem'>Disponibilizada em {nc.br(i['data'])} · "
                    f"{esc(i.get('tipo'))} · {esc(i.get('documento'))} · {esc(i.get('classe'))}</span>",
                    unsafe_allow_html=True)
        partes = " · ".join(f"{p['nome']} ({p['polo']})" if p.get("polo") else p["nome"] for p in i.get("partes", [])[:4])
        if partes:
            st.caption(f"Partes: {partes}" + (f"  ·  Cliente: **{proc.get('cliente')}**" if proc.get("cliente") else ""))
        st.write(nc.resumo(i["texto"], 320))
        if proc and not proc.get("cliente") and i.get("partes"):
            nomes = [p["nome"] for p in i["partes"]]
            cli = st.selectbox("👤 Quem é seu cliente neste processo? (preenche as petições)", [""] + nomes,
                               format_func=lambda x: x or "— escolher —", key=f"cli_i_{chave}")
            if cli:
                polo = next((p.get("polo") for p in i["partes"] if p["nome"] == cli), "")
                outro = next((p["nome"] for p in i["partes"] if p["nome"] != cli and (not polo or p.get("polo") != polo)), "")
                proc["cliente"], proc["parte_contraria"] = cli, proc.get("parte_contraria") or outro
                garantir_cliente(cli, proc)
                salvar(f"Cliente salvo: {cli}.")
                st.rerun()
        with st.expander("Ler a intimação completa"):
            st.markdown(f"<div class='texto-intim'>{esc(i['texto'])}</div>", unsafe_allow_html=True)
        b = st.columns([1, 1, 1, 1])
        with b[0].popover("⏰ Criar prazo", width="stretch"):
            formulario_prazo(i, a, chave)
        if b[1].button("📝 Gerar petição", key=f"gp_{chave}", width="stretch"):
            r = criar_rascunho(i, i["processo"], a["modelo"], a["peca"])
            i["lida"] = True
            salvar("Rascunho criado. Revise antes de protocolar.")
            ir("peticoes", rascunho_aberto=r["id"])
            st.rerun()
        if not i.get("lida"):
            if b[2].button("✅ Marcar lida", key=f"ml_{chave}", width="stretch"):
                i["lida"] = True
                salvar()
                st.rerun()
        elif b[2].button("↩️ Marcar não lida", key=f"mn_{chave}", width="stretch"):
            i["lida"] = False
            salvar()
            st.rerun()
        if i.get("link"):
            b[3].link_button("🔗 Abrir documento", i["link"], width="stretch")
        else:
            b[3].link_button("🔗 Ver no DJEN", nc.DJEN_SITE, width="stretch")


def pagina_intimacoes():
    topo()
    st.markdown("### 🔔 Intimações")
    st.caption("Fonte: Diário de Justiça Eletrônico Nacional (CNJ), pesquisa pública pelo número da OAB. "
               "Toda intimação traz a peça e o prazo sugeridos: confira sempre antes de protocolar.")
    c1, c2, c3, c4 = st.columns([1.1, 1.6, 1.8, 1])
    situ = c1.segmented_control("Situação", ["Não lidas", "Todas"], default="Não lidas", key="f_sit") or "Todas"
    orig = c2.segmented_control("Origem", ["Todas", "Minhas", "Parcerias"], default="Todas", key="f_ori") or "Todas"
    termo = nc.sem_acento(c3.text_input("Buscar", placeholder="nº do processo, parte, palavra...", key="f_busca"))
    with c4.popover("🔄 Buscar período", width="stretch"):
        dias = st.number_input("Últimos quantos dias?", 1, 90, 30)
        if st.button("Buscar", type="primary"):
            capturar_agora(int(dias))
            st.rerun()

    def filtro(i):
        if situ == "Não lidas" and i.get("lida"):
            return False
        if orig == "Minhas" and i.get("origem") != "patrona":
            return False
        if orig == "Parcerias" and i.get("origem") == "patrona":
            return False
        if termo:
            alvo = nc.sem_acento(" ".join([i["processo"], i["processo_fmt"], i["texto"], i["orgao"],
                                           " ".join(p["nome"] for p in i.get("partes", [])), cliente_proc(i["processo"])]))
            return termo in alvo or nc.so_digitos(termo) and nc.so_digitos(termo) in i["processo"]
        return True

    lista = intimacoes_ordenadas(filtro)
    if lista and situ == "Não lidas" and st.button(f"✅ Marcar as {len(lista)} como lidas"):
        for i in lista:
            i["lida"] = True
        salvar("Todas marcadas como lidas.")
        st.rerun()
    if not lista:
        st.success("Nenhuma intimação pendente com esses filtros. 🎉")
    for n, i in enumerate(lista[:60]):
        cartao_intimacao(i, f"{i['id']}_{n}")
    if len(lista) > 60:
        st.caption(f"Mostrando 60 de {len(lista)}. Use a busca para achar as outras.")


# ═════════════ Processos ═════════════
COLS_PROC = {"numero_fmt": "Processo", "cliente": "Cliente", "parte_contraria": "Parte contrária", "tribunal": "Tribunal",
             "orgao": "Órgão / Vara", "tipo": "Tipo", "parceiro": "Parceiro(a)", "honorarios": "Honorários / divisão",
             "status": "Situação", "ultima_mov": "Última intimação", "observacoes": "Observações"}


def tabela_processos(filtro, chave):
    lista = [p for p in banco["processos"].values() if filtro(p)]
    if not lista:
        st.caption("Nenhum processo aqui ainda.")
        return
    df = pd.DataFrame([{**{v: p.get(k, "") for k, v in COLS_PROC.items()}, "_num": p["numero"]} for p in lista])
    df["Última intimação"] = pd.to_datetime(df["Última intimação"], errors="coerce").dt.date
    df = df.sort_values("Última intimação", ascending=False, na_position="last").set_index("_num")
    editado = st.data_editor(
        df, key=f"ed_{chave}", width="stretch", hide_index=True,
        column_config={
            "Processo": st.column_config.TextColumn(disabled=True, width="medium"),
            "Tipo": st.column_config.SelectboxColumn(options=["Patrona", "Parceria"], required=True),
            "Situação": st.column_config.SelectboxColumn(options=["Ativo", "Suspenso", "Arquivado"], required=True),
            "Última intimação": st.column_config.DateColumn(format="DD/MM/YYYY", disabled=True),
            "Observações": st.column_config.TextColumn(width="large"),
        })
    if st.button("💾 Salvar alterações", key=f"sv_{chave}", type="primary"):
        inv = {v: k for k, v in COLS_PROC.items()}
        for num, linha in editado.iterrows():
            for col, val in linha.items():
                campo = inv.get(col)
                if campo and campo not in ("numero_fmt", "ultima_mov"):
                    banco["processos"][num][campo] = "" if pd.isna(val) else str(val)
        salvar("Processos atualizados.")
        st.rerun()


def ficha_processo():
    nums = sorted(banco["processos"], key=lambda n: banco["processos"][n].get("ultima_mov") or "", reverse=True)
    if not nums:
        return
    st.markdown("#### 🔎 Ficha do processo")
    num = st.selectbox("Processo", nums, format_func=lambda n: f"{nome_proc(n)} · {cliente_proc(n) or 'sem cliente'}",
                       key="ficha_num")
    p = banco["processos"][num]
    with st.container(border=True, key="card_ficha"):
        c1, c2 = st.columns([2, 1])
        c1.markdown(f"**{esc(p.get('numero_fmt'))}** · {esc(p.get('tribunal'))} · {esc(p.get('orgao'))}  \n"
                    f"{esc(p.get('classe'))}")
        c2.markdown(f"<div style='text-align:right'><span class='chip'>{esc(p.get('tipo'))}</span>"
                    f"<span class='chip cinza'>{esc(p.get('status'))}</span></div>", unsafe_allow_html=True)
        partes = [x["nome"] for x in p.get("partes", [])]
        if partes:
            c1, c2 = st.columns(2)
            cli = c1.selectbox("Quem é o(a) cliente?", [""] + partes, format_func=lambda x: x or "— escolher —",
                               index=(partes.index(p["cliente"]) + 1) if p.get("cliente") in partes else 0, key=f"cli_{num}")
            contra = c2.selectbox("Parte contrária", [""] + partes, format_func=lambda x: x or "— escolher —",
                                  index=(partes.index(p["parte_contraria"]) + 1) if p.get("parte_contraria") in partes else 0,
                                  key=f"con_{num}")
            if (cli and cli != p.get("cliente")) or (contra and contra != p.get("parte_contraria")):
                if st.button("💾 Salvar partes", key=f"svp_{num}"):
                    p["cliente"], p["parte_contraria"] = cli or p.get("cliente", ""), contra or p.get("parte_contraria", "")
                    garantir_cliente(p["cliente"], p)
                    salvar("Partes salvas.")
                    st.rerun()
        t1, t2, t3 = st.tabs(["🔔 Intimações", "⏰ Prazos", "📝 Petições"])
        with t1:
            for i in intimacoes_ordenadas(lambda i: i["processo"] == num):
                st.markdown(f"**{nc.br(i['data'])}** · {esc(i.get('tipo'))} · {esc(nc.analisar(i)['peca'])}")
                st.caption(nc.resumo(i["texto"], 400))
        with t2:
            for pz in sorted((x for x in banco["prazos"] if x["processo"] == num), key=lambda x: x["vencimento"]):
                st.markdown(f"{'✅' if pz['status'] == 'Cumprido' else '⏰'} **{nc.br(pz['vencimento'])}** · {esc(pz['descricao'])}")
        with t3:
            for r in (x for x in banco["rascunhos"] if x["processo"] == num):
                st.button(f"📝 {r['titulo']} · {r['criado'][:10]}", key=f"fr_{r['id']}", on_click=ir,
                          args=("peticoes",), kwargs={"rascunho_aberto": r["id"]})


def pagina_processos():
    topo()
    st.markdown("### 📁 Processos")
    st.caption("Os processos entram sozinhos a cada intimação nova. Intimação pela OAB de um parceiro vira processo de "
               "**parceria**. Edite a tabela (cliente, parte contrária, honorários) e clique em Salvar.")
    t1, t2, t3, t4 = st.tabs(["⚖️ Meu patrocínio", "🤝 Parcerias", "🗄️ Arquivados", "➕ Novo processo"])
    with t1:
        tabela_processos(lambda p: p.get("tipo") == "Patrona" and p.get("status") != "Arquivado", "pat")
    with t2:
        tabela_processos(lambda p: p.get("tipo") == "Parceria" and p.get("status") != "Arquivado", "par")
    with t3:
        tabela_processos(lambda p: p.get("status") == "Arquivado", "arq")
    with t4, st.form("novo_proc", clear_on_submit=True):
        c1, c2 = st.columns(2)
        num = c1.text_input("Número do processo (CNJ)", placeholder="0000000-00.0000.0.00.0000")
        tipo = c2.selectbox("Tipo", ["Patrona", "Parceria"])
        cli = c1.text_input("Cliente")
        contra = c2.text_input("Parte contrária")
        trib = c1.text_input("Tribunal", placeholder="TJPE, TRT6, TRF5...")
        orgao = c2.text_input("Órgão / Vara")
        parc = c1.text_input("Parceiro(a) (se for parceria)")
        hon = c2.text_input("Honorários / divisão", placeholder="ex.: 30% êxito, 50/50 com parceiro")
        obs = st.text_area("Observações")
        if st.form_submit_button("Adicionar processo", type="primary"):
            d = nc.so_digitos(num)
            if not d:
                st.error("Informe o número do processo.")
            else:
                banco["processos"][d] = {"numero": d, "numero_fmt": nc.mascara_cnj(d), "cliente": cli, "parte_contraria": contra,
                                         "tribunal": trib, "orgao": orgao, "classe": "", "tipo": tipo, "parceiro": parc,
                                         "honorarios": hon, "status": "Ativo", "observacoes": obs, "partes": [],
                                         "criado": HOJE.isoformat()}
                garantir_cliente(cli, banco["processos"][d])
                salvar("Processo adicionado.")
                st.rerun()
    st.write("")
    ficha_processo()


# ═════════════ Prazos ═════════════
def pagina_prazos():
    topo()
    st.markdown("### ⏰ Controle de prazos")
    st.caption("Contagem em dias úteis (CPC, art. 219), com publicação no 1º dia útil após a disponibilização no DJEN e "
               "início no dia útil seguinte (CPC, art. 224; Lei 11.419/2006, art. 4º). Suspende de 20/12 a 20/01 "
               "(CPC, art. 220). Feriados locais você cadastra em ⚙️ Configurações. **Confira sempre no sistema do tribunal.**")
    abertos = prazos_abertos()
    vencidos = [p for p in abertos if dias_para(p["vencimento"]) < 0]
    if vencidos:
        st.error(f"⚠️ {len(vencidos)} prazo(s) com data já passada. Marque como cumprido ou ajuste.")
    t1, t2, t3 = st.tabs([f"Em aberto ({len(abertos)})", "Cumpridos", "➕ Novo prazo"])
    with t1:
        for p in abertos:
            rot, cor, cls = rotulo_prazo(p["vencimento"])
            with st.container(border=True, key=f"card_pz_{p['id']}"):
                c1, c2, c3 = st.columns([4, 1.2, 1.2], vertical_alignment="center")
                c1.markdown(f"<span class='chip {cls}'>{rot}</span><span class='chip cinza'>{esc(p.get('tipo', 'Prazo'))}</span> "
                            f"**{esc(p['descricao'])}**  \n<span style='color:{APAGADO};font-size:.85rem'>"
                            f"{esc(nome_proc(p['processo']))} · {esc(cliente_proc(p['processo']))} · vence "
                            f"{nc.br(p['vencimento'])} {esc(p.get('hora', ''))}</span>", unsafe_allow_html=True)
                if c2.button("✅ Cumprido", key=f"cp_{p['id']}", width="stretch"):
                    p["status"], p["cumprido_em"] = "Cumprido", HOJE.isoformat()
                    salvar("Prazo cumprido.")
                    st.rerun()
                if c3.button("📝 Petição", key=f"pp_{p['id']}", width="stretch"):
                    intim = banco["intimacoes"].get(p.get("origem"))
                    modelo = nc.MODELO_DA_PECA.get(p.get("peca") or "", "Manifestação simples")
                    r = criar_rascunho(intim, p["processo"], modelo, p.get("peca") or p["descricao"])
                    salvar("Rascunho criado.")
                    ir("peticoes", rascunho_aberto=r["id"])
                    st.rerun()
        if not abertos:
            st.success("Nenhum prazo em aberto.")
    with t2:
        feitos = sorted((p for p in banco["prazos"] if p.get("status") == "Cumprido"), key=lambda p: p["vencimento"], reverse=True)
        for p in feitos[:50]:
            c1, c2 = st.columns([5, 1], vertical_alignment="center")
            c1.markdown(f"✅ **{nc.br(p['vencimento'])}** · {esc(p['descricao'])} · {esc(nome_proc(p['processo']))}")
            if c2.button("Reabrir", key=f"ra_{p['id']}"):
                p["status"] = "Aberto"
                salvar()
                st.rerun()
    with t3:
        nums = list(banco["processos"])
        c1, c2 = st.columns(2)
        proc = c1.selectbox("Processo", [""] + nums, format_func=lambda n: f"{nome_proc(n)} · {cliente_proc(n)}" if n else "—",
                            key="np_proc")
        desc = c2.text_input("Descrição", placeholder="ex.: Contestação, Réplica, Audiência", key="np_desc")
        tipo = c1.selectbox("Tipo", ["Prazo", "Audiência", "Compromisso"], key="np_tipo")
        if tipo == "Prazo":
            base = c2.date_input("Data da disponibilização no DJEN", value=HOJE, format="DD/MM/YYYY", key="np_base")
            c3, c4 = st.columns(2)
            dias = c3.number_input("Dias", 1, 120, 15, key="np_dias")
            uteis = c4.toggle("Dias úteis", True, key="np_uteis")
            ext, mov = extras()
            pub, ini, venc = nc.calcular_prazo(base, int(dias), uteis, ext, mov)
            st.info(f"Publicação: **{nc.br(pub)}** · Início: **{nc.br(ini)}** · Vencimento: **{nc.br(venc)}**")
            hora = ""
        else:
            venc = c2.date_input("Data", value=HOJE, format="DD/MM/YYYY", key="np_data")
            hora, ini = st.text_input("Hora", key="np_hora"), None
        if st.button("Salvar", type="primary", key="np_ok"):
            if not desc:
                st.error("Escreva a descrição.")
            else:
                novo_prazo(proc, desc, venc, ini, tipo=tipo, hora=hora)
                salvar("Salvo.")
                st.rerun()


# ═════════════ Agenda ═════════════
def pagina_agenda():
    topo()
    st.markdown("### 📅 Agenda")
    st.session_state.setdefault("ag_mes", (HOJE.year, HOJE.month))
    ano, mes = st.session_state.ag_mes
    c1, c2, c3 = st.columns([1, 3, 1], vertical_alignment="center")
    if c1.button("◀ Mês anterior"):
        st.session_state.ag_mes = (ano - 1, 12) if mes == 1 else (ano, mes - 1)
        st.rerun()
    c2.markdown(f"<h3 style='text-align:center;margin:0'>{MESES[mes - 1]} {ano}</h3>", unsafe_allow_html=True)
    if c3.button("Próximo mês ▶"):
        st.session_state.ag_mes = (ano + 1, 1) if mes == 12 else (ano, mes + 1)
        st.rerun()
    por_dia = {}
    for p in banco["prazos"]:
        por_dia.setdefault(nc.para_data(p["vencimento"]), []).append(p)
    for t in banco["tarefas"]:
        if t.get("data") and not t.get("feita"):
            por_dia.setdefault(nc.para_data(t["data"]), []).append({"descricao": "☑ " + t["titulo"], "tipo": "Tarefa", "status": ""})
    linhas = ""
    for semana in calendar.Calendar(firstweekday=6).monthdatescalendar(ano, mes):
        tds = ""
        for d in semana:
            evs = ""
            for p in por_dia.get(d, [])[:4]:
                cls = "ok" if p.get("status") == "Cumprido" else ("aud" if p.get("tipo") in ("Audiência", "Compromisso", "Tarefa") else "")
                evs += f"<div class='ev {cls}' title='{esc(p['descricao'])}'>{esc(p.get('hora', ''))} {esc(p['descricao'])}</div>"
            estilo = " style='opacity:.4'" if d.month != mes else ""
            tds += f"<td class='{'hoje' if d == HOJE else ''}'{estilo}><div class='n'>{d.day}</div>{evs}</td>"
        linhas += f"<tr>{tds}</tr>"
    cab = "".join(f"<th>{d}</th>" for d in ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"])
    with st.container(border=True, key="card_agenda"):
        st.markdown(f"<table class='cal calg'><tr>{cab}</tr>{linhas}</table>", unsafe_allow_html=True)
    st.caption("🔴 prazos · 🔵 audiências, compromissos e tarefas · 🟢 cumpridos")


# ═════════════ Tarefas ═════════════
def pagina_tarefas():
    topo()
    st.markdown("### ☑️ Tarefas")
    with st.form("nova_tarefa", clear_on_submit=True):
        c1, c2, c3 = st.columns([3, 2, 1.2])
        tit = c1.text_input("Nova tarefa", placeholder="ex.: Pedir documentos ao cliente")
        proc = c2.selectbox("Processo (opcional)", [""] + list(banco["processos"]),
                            format_func=lambda n: f"{nome_proc(n)} · {cliente_proc(n)}" if n else "—")
        data = c3.date_input("Para quando", value=None, format="DD/MM/YYYY")
        if st.form_submit_button("Adicionar", type="primary") and tit:
            banco["tarefas"].append({"id": nc.novo_id(), "titulo": tit, "processo": proc,
                                     "data": data.isoformat() if data else None, "feita": False})
            salvar("Tarefa adicionada.")
            st.rerun()
    pend = sorted((t for t in banco["tarefas"] if not t.get("feita")), key=lambda t: t.get("data") or "9999")
    with st.container(border=True, key="card_tlist"):
        cabecalho("Pendentes", str(len(pend)))
        for t in pend:
            c1, c2 = st.columns([6, 1], vertical_alignment="center")
            extra = " · ".join(x for x in [nc.br(t.get("data")), nome_proc(t["processo"]) if t.get("processo") else ""] if x)
            if c1.checkbox(f"{t['titulo']}" + (f"  —  {extra}" if extra else ""), key=f"tk_{t['id']}"):
                t["feita"] = True
                salvar("Concluída.")
                st.rerun()
            if c2.button("🗑️", key=f"td_{t['id']}"):
                banco["tarefas"].remove(t)
                nc.apagar(banco, t["id"])
                salvar()
                st.rerun()
        if not pend:
            st.caption("Nenhuma tarefa pendente.")
    feitas = [t for t in banco["tarefas"] if t.get("feita")]
    if feitas:
        with st.expander(f"Concluídas ({len(feitas)})"):
            for t in feitas[-30:]:
                st.markdown(f"~~{esc(t['titulo'])}~~")
            if st.button("Limpar concluídas"):
                for t in banco["tarefas"]:
                    if t.get("feita"):
                        nc.apagar(banco, t["id"])
                banco["tarefas"] = [t for t in banco["tarefas"] if not t.get("feita")]
                salvar()
                st.rerun()


# ═════════════ Petições ═════════════
def editor_rascunho(r):
    intim = banco["intimacoes"].get(r.get("intimacao"))
    with st.container(border=True, key="card_rasc"):
        c1, c2 = st.columns([3, 1], vertical_alignment="center")
        r["titulo"] = c1.text_input("Título", r["titulo"], key=f"rt_{r['id']}")
        status = c2.selectbox("Situação", ["Rascunho", "Revisada", "Protocolada"],
                              index=["Rascunho", "Revisada", "Protocolada"].index(r.get("status", "Rascunho")), key=f"rs_{r['id']}")
        texto = st.text_area("Texto da petição (os trechos [COMPLETAR] são o que falta você escrever)", r["texto"],
                             height=520, key=f"rx_{r['id']}")
        falta = texto.count("[COMPLETAR")
        st.caption(f"{'⚠️ ' + str(falta) + ' trecho(s) [COMPLETAR] ainda em aberto.' if falta else '✅ Nenhum [COMPLETAR] em aberto.'}")
        b = st.columns(4)
        if b[0].button("💾 Salvar", type="primary", width="stretch", key=f"rsv_{r['id']}"):
            r["texto"], r["status"] = texto, status
            salvar("Petição salva.")
            st.rerun()
        b[1].download_button("⬇️ Baixar Word (.docx)", nc.gerar_docx(r["titulo"], texto),
                             file_name=f"{r['titulo'][:60].replace('/', '-')}.docx", width="stretch",
                             mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        b[2].download_button("⬇️ Baixar texto", texto.encode("utf-8"), file_name=f"{r['titulo'][:60].replace('/', '-')}.txt",
                             width="stretch")
        if b[3].button("🗑️ Apagar", width="stretch", key=f"rdl_{r['id']}"):
            banco["rascunhos"].remove(r)
            nc.apagar(banco, r["id"])
            st.session_state.pop("rascunho_aberto", None)
            salvar("Rascunho apagado.")
            st.rerun()
    modelos = nc.ler_modelos(banco)
    campos = nc.campos_do_processo(banco, intim=intim, proc=banco["processos"].get(r["processo"]))
    with st.expander("🤖 Quer que o Claude escreva a peça completa? Copie este pedido e cole no chat do Claude"):
        st.caption("Clique no ícone de copiar no canto do quadro. Depois cole a resposta aqui no texto acima e revise.")
        st.code(nc.prompt_para_claude(intim, campos, r.get("peca", r["modelo"]),
                                      (modelos.get(r["modelo"]) or {}).get("texto", texto)), language=None, wrap_lines=True)
    if intim:
        with st.expander("🔔 Intimação de origem"):
            st.markdown(f"<div class='texto-intim'>{esc(intim['texto'])}</div>", unsafe_allow_html=True)


def pagina_peticoes():
    topo()
    st.markdown("### 📝 Petições")
    modelos = nc.ler_modelos(banco)
    t1, t2, t3 = st.tabs([f"📄 Rascunhos ({len(banco['rascunhos'])})", "➕ Nova petição", "📚 Modelos"])
    with t1:
        if not banco["rascunhos"]:
            st.info("Nenhum rascunho ainda. Em 🔔 Intimações, clique em **📝 Gerar petição** na intimação: o app já "
                    "escolhe o modelo e preenche processo, vara, partes e o trecho da intimação.")
        else:
            ids = [r["id"] for r in banco["rascunhos"]]
            aberto = st.session_state.get("rascunho_aberto")
            idx = ids.index(aberto) if aberto in ids else 0
            rid = st.selectbox("Rascunho", ids, index=idx, key="sel_rasc",
                               format_func=lambda x: next(f"{r['titulo']} · {r.get('status', 'Rascunho')} · {r['criado'][:10]}"
                                                          for r in banco["rascunhos"] if r["id"] == x))
            st.session_state.rascunho_aberto = rid
            editor_rascunho(next(r for r in banco["rascunhos"] if r["id"] == rid))
    with t2:
        c1, c2 = st.columns(2)
        proc = c1.selectbox("Processo", [""] + list(banco["processos"]),
                            format_func=lambda n: f"{nome_proc(n)} · {cliente_proc(n)}" if n else "— sem processo —", key="nv_proc")
        modelo = c2.selectbox("Modelo", list(modelos), key="nv_mod")
        st.markdown(f"<div class='texto-intim'>{esc(modelos[modelo]['texto'][:1500])}</div>", unsafe_allow_html=True)
        if st.button("Criar rascunho com este modelo", type="primary"):
            r = criar_rascunho(None, proc, modelo)
            salvar("Rascunho criado.")
            st.session_state.rascunho_aberto = r["id"]
            st.rerun()
    with t3:
        st.caption("Os campos entre chaves duplas são preenchidos sozinhos: {{processo}}, {{orgao}}, {{tribunal}}, {{cliente}}, "
                   "{{parte_contraria}}, {{advogada}}, {{oab}}, {{cidade}}, {{data}}, {{data_intimacao}}, {{resumo_intimacao}}, {{endereco_escritorio}}.")
        nome = st.selectbox("Modelo", list(modelos) + ["➕ Criar modelo novo"], key="md_sel")
        if nome == "➕ Criar modelo novo":
            novo = st.text_input("Nome do modelo", placeholder="ex.: Procuração ad judicia, Contestação trabalhista")
            txt = st.text_area("Texto", height=420, value="EXCELENTÍSSIMO(A) SENHOR(A) JUIZ(A) DA {{orgao}}\n\nProcesso nº {{processo}}\n\n"
                               "{{cliente}}, ...\n\n{{cidade}}, {{data}}.\n\n{{advogada}}\n{{oab}}")
            if st.button("Salvar modelo", type="primary") and novo:
                banco["modelos_custom"][novo] = {"texto": txt}
                salvar("Modelo salvo.")
                st.rerun()
        else:
            m = modelos[nome]
            txt = st.text_area("Texto do modelo", m["texto"], height=480, key=f"md_{nome}")
            c1, c2 = st.columns(2)
            if c1.button("💾 Salvar (como meu modelo)", type="primary"):
                banco["modelos_custom"][nome] = {"texto": txt}
                salvar("Modelo salvo. Ele passa a valer no lugar do padrão.")
                st.rerun()
            if m["proprio"] and c2.button("🗑️ Apagar meu modelo / voltar ao padrão"):
                banco["modelos_custom"].pop(nome, None)
                nc.apagar(banco, nome)
                salvar("Modelo removido.")
                st.rerun()


# ═════════════ Parceiros ═════════════
def processos_do_parceiro(nome):
    return [p for p in banco["processos"].values() if p.get("tipo") == "Parceria" and nc.sem_acento(p.get("parceiro")) == nc.sem_acento(nome)]


def pagina_parceiros():
    topo()
    st.markdown("### 🤝 Advogados parceiros")
    st.caption("Cadastre aqui seus parceiros. Com **Buscar intimações** ligado, o painel também busca as intimações da OAB "
               "do parceiro e coloca esses processos na aba Parcerias.")
    parceiros = cfg.get("parceiros") or []
    procs_parc = [p for p in banco["processos"].values() if p.get("tipo") == "Parceria"]
    k = st.columns(3)
    with k[0]:
        kpi("🤝", "#EEF4FF", "Parceiros cadastrados", len(parceiros), f"<b>{sum(1 for p in parceiros if p.get('buscar', True))}</b> com busca de intimações")
    with k[1]:
        kpi("📁", "#FEF3C7", "Processos em parceria", len(procs_parc), f"<b>{sum(1 for p in procs_parc if p.get('status') != 'Arquivado')}</b> ativos")
    with k[2]:
        n = sum(1 for i in banco["intimacoes"].values() if i.get("origem") != "patrona")
        kpi("🔔", "#FEE2E2", "Intimações via parceiros", n, "pelas OABs cadastradas")
    st.write("")
    with st.container(border=True, key="card_parc"):
        cabecalho("Cadastro", "clique na última linha vazia para adicionar")
        df = pd.DataFrame(parceiros, columns=["nome", "numero", "uf", "telefone", "email", "area", "divisao", "buscar", "obs"])
        df["buscar"] = df["buscar"].map(lambda v: v is not False)
        for col in ["nome", "numero", "uf", "telefone", "email", "area", "divisao", "obs"]:
            df[col] = df[col].fillna("").astype(str)
        ed = st.data_editor(df, num_rows="dynamic", key="ed_parceiros", width="stretch", hide_index=True, column_config={
            "nome": st.column_config.TextColumn("Nome", required=True, width="medium"),
            "numero": st.column_config.TextColumn("Nº OAB"), "uf": st.column_config.TextColumn("UF", default="PE", max_chars=2),
            "telefone": st.column_config.TextColumn("Telefone / WhatsApp"), "email": st.column_config.TextColumn("E-mail"),
            "area": st.column_config.TextColumn("Área de atuação"),
            "divisao": st.column_config.TextColumn("Divisão de honorários", help="ex.: 50/50, 30% para o parceiro"),
            "buscar": st.column_config.CheckboxColumn("Buscar intimações", default=True),
            "obs": st.column_config.TextColumn("Observações", width="medium")})
        if st.button("💾 Salvar parceiros", type="primary"):
            novos = []
            for _, l in ed.iterrows():
                nome = str(l.get("nome") or "").strip()
                if not nome or nome == "nan":
                    continue
                item = {c: ("" if pd.isna(l.get(c)) else str(l.get(c)).strip()) for c in ["nome", "telefone", "email", "area", "divisao", "obs"]}
                item.update({"numero": nc.so_digitos(l.get("numero") if not pd.isna(l.get("numero")) else ""),
                             "uf": (str(l.get("uf") or "PE") if not pd.isna(l.get("uf")) else "PE").upper()[:2],
                             "buscar": bool(l.get("buscar")) if not pd.isna(l.get("buscar")) else True})
                novos.append(item)
            cfg["parceiros"] = novos
            salvar("Parceiros salvos.")
            st.rerun()
    for p in parceiros:
        procs = processos_do_parceiro(p["nome"])
        with st.container(border=True, key=f"card_pc_{nc.so_digitos(p.get('numero')) or nc.sem_acento(p['nome']).replace(' ', '_')}"):
            c1, c2 = st.columns([3, 1], vertical_alignment="center")
            c1.markdown(f"**{esc(p['nome'])}** · OAB/{esc(p.get('uf'))} {esc(p.get('numero'))} · {esc(p.get('area'))}  \n"
                        f"<span style='color:{APAGADO};font-size:.85rem'>Divisão: {esc(p.get('divisao') or '—')} · "
                        f"{len(procs)} processo(s) em parceria</span>", unsafe_allow_html=True)
            tel = nc.so_digitos(p.get("telefone"))
            if tel:
                c2.link_button("💬 WhatsApp", f"https://wa.me/{tel if tel.startswith('55') else '55' + tel}", width="stretch")
            if procs:
                for pr in procs:
                    st.caption(f"📁 {pr.get('numero_fmt')} · {cliente_proc(pr['numero']) or 'sem cliente'} · {pr.get('status')}")


# ═════════════ Clientes e prospecção ═════════════
def lista_clientes(filtro=None):
    return sorted((c for c in banco["clientes"].values() if filtro is None or filtro(c)),
                  key=lambda c: c.get("atualizado") or "", reverse=True)


def novo_cliente(nome, etapa="Primeiro contato", **campos):
    c = {"id": nc.novo_id(), "nome": nome.strip(), "etapa": etapa, "segmento": "", "origem": "", "telefone": "",
         "email": "", "cpf_cnpj": "", "rg": "", "estado_civil": "", "profissao": "", "nacionalidade": "",
         "endereco": "", "assunto": "", "valor": "", "honorarios": "", "proximo_passo": "", "data_proximo": None,
         "data_contato": HOJE.isoformat(), "data_fechamento": HOJE.isoformat() if etapa == "Contrato fechado" else None,
         "obs": "", "documentos": [], "atualizado": dt.datetime.now().isoformat(timespec="minutes")}
    c.update({k: v for k, v in campos.items() if v not in (None, "")})
    banco["clientes"][c["id"]] = c
    return c


def garantir_cliente(nome, proc=None):
    """Quem já tem processo com você vira cliente com contrato fechado (se ainda não estiver cadastrado)."""
    if not nome:
        return None
    c = next((c for c in banco["clientes"].values() if nc.sem_acento(c["nome"]) == nc.sem_acento(nome)), None)
    if not c:
        c = novo_cliente(nome.title() if nome.isupper() else nome, "Contrato fechado", origem="Processo existente")
    if proc is not None:
        proc["cliente_id"] = c["id"]
    return c


def processos_do_cliente(c):
    return [p for p in banco["processos"].values()
            if p.get("cliente_id") == c["id"] or (p.get("cliente") and nc.sem_acento(p["cliente"]) == nc.sem_acento(c["nome"]))]


def mudar_etapa(c, etapa):
    c["etapa"] = etapa
    c["atualizado"] = dt.datetime.now().isoformat(timespec="minutes")
    if etapa == "Contrato fechado":
        c["data_fechamento"] = HOJE.isoformat()
    salvar(f"{c['nome']}: {etapa}.")


def valor_num(v):
    t = str(v or "").replace("R$", "").replace(" ", "")
    if "," in t or re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return 0.0


def moeda(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def form_novo_contato(chave, etapa_padrao="Primeiro contato"):
    with st.form(f"novo_contato_{chave}", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nome = c1.text_input("Nome *")
        tel = c2.text_input("Telefone / WhatsApp")
        email = c3.text_input("E-mail")
        seg = c1.selectbox("Segmento", cfg.get("segmentos") or ["Outros"])
        orig = c2.selectbox("Como chegou", nc.ORIGENS)
        etapa = c3.selectbox("Etapa", nc.ETAPAS[:5], index=nc.ETAPAS.index(etapa_padrao))
        assunto = st.text_input("Assunto / caso", placeholder="ex.: aposentadoria negada pelo INSS, revisão de juros do financiamento")
        c1, c2, c3 = st.columns(3)
        valor = c1.text_input("Valor da proposta (R$)")
        prox = c2.text_input("Próximo passo", placeholder="ex.: enviar proposta, ligar")
        data = c3.date_input("Quando", value=None, format="DD/MM/YYYY")
        if st.form_submit_button("Adicionar", type="primary"):
            if not nome.strip():
                st.error("Escreva o nome.")
                return
            novo_cliente(nome, etapa, telefone=tel, email=email, segmento=seg, origem=orig, assunto=assunto, valor=valor,
                         proximo_passo=prox, data_proximo=data.isoformat() if data else None)
            salvar(f"{nome} adicionado(a).")
            st.rerun()


def cartao_lead(c, chave):
    with st.container(border=True, key=f"card_ld_{chave}"):
        prox = ""
        if c.get("proximo_passo") or c.get("data_proximo"):
            atrasado = c.get("data_proximo") and nc.para_data(c["data_proximo"]) < HOJE
            prox = (f"<div class='sub' style='color:{VERMELHO if atrasado else APAGADO}'>➡ {esc(c.get('proximo_passo'))} "
                    f"{nc.br(c.get('data_proximo'))}</div>")
        st.markdown(f"<div class='tit'>{esc(c['nome'])}</div><span class='chip'>{esc(c.get('segmento') or 'sem segmento')}</span>"
                    f"<span class='chip cinza'>{esc(c.get('origem'))}</span>"
                    f"<div class='sub'>{esc(nc.resumo(c.get('assunto'), 80))}</div>"
                    f"{'<div class=sub><b>' + moeda(valor_num(c.get('valor'))) + '</b></div>' if valor_num(c.get('valor')) else ''}{prox}",
                    unsafe_allow_html=True)
        i = nc.ETAPAS.index(c["etapa"]) if c["etapa"] in nc.ETAPAS else 0
        b1, b2, b3 = st.columns(3)
        if i > 0 and b1.button("◀", key=f"lv_{chave}", help="Voltar etapa", width="stretch"):
            mudar_etapa(c, nc.ETAPAS[i - 1])
            st.rerun()
        if i < 4 and b2.button("▶", key=f"la_{chave}", help=f"Avançar para {nc.ETAPAS[i + 1]}", width="stretch"):
            mudar_etapa(c, nc.ETAPAS[i + 1])
            st.rerun()
        b3.button("📂", key=f"lp_{chave}", help="Abrir a pasta do cliente", width="stretch", on_click=ir,
                  args=("clientes",), kwargs={"cliente_aberto": c["id"], "aba_clientes": "pasta", "sel_cliente": c["id"]})


def pagina_prospeccao():
    topo()
    st.markdown("### 🎯 Prospecção e fechamento de contratos")
    segs = cfg.get("segmentos") or []
    seg = st.pills("Segmento", ["Todos"] + segs, default="Todos", key="f_seg") or "Todos"
    todos = [c for c in banco["clientes"].values() if seg == "Todos" or c.get("segmento") == seg]
    abertos = [c for c in todos if c["etapa"] in nc.ETAPAS_ABERTAS]
    fechados = [c for c in todos if c["etapa"] == "Contrato fechado" and c.get("origem") != "Processo existente"]
    perdidos = [c for c in todos if c["etapa"] == "Perdido"]
    mes = [c for c in fechados if (c.get("data_fechamento") or "")[:7] == HOJE.isoformat()[:7]]
    conv = len(fechados) / (len(fechados) + len(perdidos)) * 100 if (fechados or perdidos) else 0
    k = st.columns(4)
    with k[0]:
        kpi("🎯", "#EEF4FF", "Em negociação", len(abertos), f"<b>{moeda(sum(valor_num(c.get('valor')) for c in abertos))}</b> em propostas")
    with k[1]:
        kpi("✍️", "#DCFCE7", "Contratos fechados no mês", len(mes), f"<b>{moeda(sum(valor_num(c.get('valor')) for c in mes))}</b>")
    with k[2]:
        kpi("📈", "#FEF3C7", "Taxa de fechamento", f"{conv:.0f}%", f"<b>{len(fechados)}</b> fechados · <b>{len(perdidos)}</b> perdidos")
    with k[3]:
        atras = sum(1 for c in abertos if c.get("data_proximo") and nc.para_data(c["data_proximo"]) <= HOJE)
        kpi("⏰", "#FEE2E2", "Retornos para hoje", atras, "contatos com próximo passo vencido")
    st.write("")
    with st.expander("➕ Novo contato / possível cliente"):
        form_novo_contato("prosp")
    cols = st.columns(5)
    for col, etapa in zip(cols, nc.ETAPAS[:5]):
        lista = [c for c in todos if c["etapa"] == etapa]
        if etapa == "Contrato fechado":
            lista = [c for c in lista if (c.get("data_fechamento") or "") >= (HOJE - dt.timedelta(days=30)).isoformat()]
        with col:
            st.markdown(f"<div class='cab'><h4>{etapa}</h4><span>{len(lista)}</span></div>", unsafe_allow_html=True)
            for n, c in enumerate(sorted(lista, key=lambda c: c.get("data_proximo") or "9999")[:15]):
                cartao_lead(c, f"{c['id']}_{n}")
            if etapa == "Negociação" and lista:
                st.caption("No ▶ o contrato é marcado como fechado.")
    if perdidos:
        with st.expander(f"✖ Perdidos ({len(perdidos)})"):
            for c in perdidos:
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"{esc(c['nome'])} · {esc(c.get('segmento'))} · {esc(c.get('obs'))[:80]}")
                if c2.button("Reabrir", key=f"rp_{c['id']}"):
                    mudar_etapa(c, "Negociação")
                    st.rerun()
    st.write("")
    with st.container(border=True, key="card_segmentos"):
        cabecalho("📊 Resultado por segmento", "o que está trazendo contrato")
        linhas = []
        for s in segs:
            g = [c for c in banco["clientes"].values() if c.get("segmento") == s and c.get("origem") != "Processo existente"]
            f = [c for c in g if c["etapa"] == "Contrato fechado"]
            p = [c for c in g if c["etapa"] == "Perdido"]
            if g:
                linhas.append({"Segmento": s, "Contatos": len(g), "Em aberto": len(g) - len(f) - len(p), "Fechados": len(f),
                               "Perdidos": len(p), "Taxa de fechamento": (len(f) / (len(f) + len(p)) * 100) if (f or p) else 0.0,
                               "Valor fechado": sum(valor_num(c.get("valor")) for c in f)})
        if linhas:
            st.dataframe(pd.DataFrame(linhas).sort_values("Fechados", ascending=False), hide_index=True, width="stretch",
                         column_config={"Taxa de fechamento": st.column_config.ProgressColumn(format="%.0f%%", min_value=0, max_value=100),
                                        "Valor fechado": st.column_config.NumberColumn(format="R$ %.2f")})
            orig = pd.DataFrame([{"Origem": c.get("origem") or "—", "Fechado": c["etapa"] == "Contrato fechado"}
                                 for c in banco["clientes"].values() if c.get("origem") != "Processo existente"])
            st.caption("De onde vêm os contatos: " + " · ".join(
                f"**{o}** {len(g)} ({int(g['Fechado'].sum())} fechados)" for o, g in orig.groupby("Origem")))
        else:
            st.caption("Os números aparecem quando você cadastrar os primeiros contatos.")


def lista_simples(clientes, chave, mostrar_fechar=False):
    if not clientes:
        st.caption("Ninguém aqui ainda.")
    for c in clientes:
        with st.container(border=True, key=f"card_cl_{chave}_{c['id']}"):
            c1, c2, c3 = st.columns([4, 1.1, 1.1], vertical_alignment="center")
            procs = processos_do_cliente(c)
            docs = len(c.get("documentos", []))
            info = (f"Fechado em {nc.br(c.get('data_fechamento'))} · " if c["etapa"] == "Contrato fechado" else f"{esc(c['etapa'])} · ")
            c1.markdown(f"**{esc(c['nome'])}** <span class='chip'>{esc(c.get('segmento') or 'sem segmento')}</span>  \n"
                        f"<span style='color:{APAGADO};font-size:.85rem'>{info}{len(procs)} processo(s) · {docs} documento(s) · "
                        f"{esc(c.get('telefone'))} · {esc(nc.resumo(c.get('assunto'), 70))}</span>", unsafe_allow_html=True)
            c2.button("📂 Pasta", key=f"ab_{chave}_{c['id']}", width="stretch", on_click=ir, args=("clientes",),
                      kwargs={"cliente_aberto": c["id"], "aba_clientes": "pasta", "sel_cliente": c["id"]})
            if mostrar_fechar and c3.button("✍️ Fechou", key=f"fc_{chave}_{c['id']}", width="stretch", help="Contrato assinado"):
                mudar_etapa(c, "Contrato fechado")
                st.rerun()


def pasta_cliente(c):
    with st.container(border=True, key="card_pasta"):
        c1, c2 = st.columns([3, 1], vertical_alignment="center")
        c1.markdown(f"<div class='ola'>📂 {esc(c['nome'])}</div><div class='ola-sub'>{esc(c.get('segmento'))} · "
                    f"{esc(c.get('origem'))} · " + (f"contrato fechado em {nc.br(c.get('data_fechamento'))}"
                    if c["etapa"] == "Contrato fechado" else f"primeiro contato em {nc.br(c.get('data_contato'))}") + "</div>",
                    unsafe_allow_html=True)
        etapa = c2.selectbox("Situação", nc.ETAPAS, index=nc.ETAPAS.index(c["etapa"]) if c["etapa"] in nc.ETAPAS else 0,
                             key=f"et_{c['id']}")
        if etapa != c["etapa"]:
            mudar_etapa(c, etapa)
            st.rerun()
    t1, t2, t3, t4 = st.tabs(["📁 Processos", "📎 Documentos", "✍️ Procuração e contrato", "👤 Dados do cliente"])
    with t1:
        procs = processos_do_cliente(c)
        for p in procs:
            prazos = [x for x in prazos_abertos() if x["processo"] == p["numero"]]
            with st.container(border=True, key=f"card_cp_{p['numero']}"):
                st.markdown(f"**{esc(p.get('numero_fmt'))}** · {esc(p.get('tribunal'))} · {esc(p.get('orgao'))} "
                            f"<span class='chip'>{esc(p.get('tipo'))}</span><span class='chip cinza'>{esc(p.get('status'))}</span>  \n"
                            f"<span style='color:{APAGADO};font-size:.85rem'>Última intimação {nc.br(p.get('ultima_mov')) or '—'}: "
                            f"{esc(p.get('ultima_mov_resumo', ''))}</span>", unsafe_allow_html=True)
                for x in prazos:
                    rot, cor, cls = rotulo_prazo(x["vencimento"])
                    st.markdown(f"<span class='chip {cls}'>{rot}</span> {esc(x['descricao'])}", unsafe_allow_html=True)
                st.button("Abrir ficha do processo", key=f"fp_{p['numero']}", on_click=ir, args=("processos",),
                          kwargs={"ficha_num": p["numero"]})
        if not procs:
            st.caption("Nenhum processo ligado a este cliente.")
        livres = [n for n, p in banco["processos"].items() if not p.get("cliente_id") and p not in procs]
        if livres:
            c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
            num = c1.selectbox("Ligar um processo a este cliente", [""] + livres, key=f"lig_{c['id']}",
                               format_func=lambda n: f"{nome_proc(n)} · {cliente_proc(n)}" if n else "— escolher —")
            if c2.button("🔗 Ligar", key=f"ligb_{c['id']}", width="stretch") and num:
                p = banco["processos"][num]
                p["cliente_id"], p["cliente"] = c["id"], c["nome"]
                salvar("Processo ligado ao cliente.")
                st.rerun()
    with t2:
        c1, c2 = st.columns([1, 2])
        tipo = c1.selectbox("Tipo de documento", nc.TIPOS_DOC, key=f"td_{c['id']}")
        envio = c2.file_uploader("Enviar arquivos (PDF, imagem, Word)", accept_multiple_files=True,
                                 key=f"up_{c['id']}_{st.session_state.get('n_envios', 0)}")
        if envio and st.button("💾 Guardar na pasta do cliente", type="primary", key=f"upb_{c['id']}"):
            for f in envio:
                nome = f"{HOJE.isoformat()}_{nc.novo_id()[:4]}_{f.name}"
                erro = nc.guardar_documento(c["id"], nome, f.getvalue())
                if erro:
                    st.session_state.aviso = (erro, "⚠️")
                c.setdefault("documentos", []).append({"arquivo": nome, "nome": f.name, "tipo": tipo, "data": HOJE.isoformat()})
            st.session_state.n_envios = st.session_state.get("n_envios", 0) + 1
            salvar(f"{len(envio)} arquivo(s) guardado(s).")
            st.rerun()
        docs = c.get("documentos", [])
        for tipo_doc in nc.TIPOS_DOC:
            grupo = [d for d in docs if d["tipo"] == tipo_doc]
            if not grupo:
                continue
            st.markdown(f"**{tipo_doc}**")
            for n, d in enumerate(grupo):
                conteudo = nc.ler_documento(c["id"], d["arquivo"])
                c1, c2, c3 = st.columns([5, 1, 1], vertical_alignment="center")
                c1.caption(f"📄 {d['nome']} · {nc.br(d['data'])}" + ("" if conteudo is not None else " · ⚠️ arquivo não encontrado"))
                if conteudo is not None:
                    c2.download_button("⬇️", conteudo, file_name=d["nome"], key=f"dl_{n}_{d['arquivo']}", width="stretch")
                if c3.button("🗑️", key=f"rm_{n}_{d['arquivo']}", width="stretch"):
                    nc.apagar_documento(c["id"], d["arquivo"])
                    docs.remove(d)
                    salvar("Documento apagado.")
                    st.rerun()
        if not docs:
            st.caption("A pasta está vazia." + (" Os arquivos ficam no computador e na cópia online (GitHub privado)."
                                                 if nc.NUVEM else f" Os arquivos ficam no seu computador em dados/clientes/{c['id']}."))
        faltam = [t for t in ["Documento pessoal", "Comprovante de residência", "Procuração", "Contrato de honorários"]
                  if not any(d["tipo"] == t for d in docs)]
        if faltam and c["etapa"] == "Contrato fechado":
            st.warning("Falta na pasta: " + ", ".join(faltam))
    with t3:
        modelos = nc.ler_modelos_cliente()
        nome_m = st.selectbox("Documento", list(modelos), key=f"mc_{c['id']}")
        if not c.get("cpf_cnpj") or not c.get("endereco"):
            st.info("Complete CPF e endereço na aba 👤 Dados do cliente para a qualificação sair completa.")
        texto = st.text_area("Texto (pode editar antes de baixar)", nc.preencher(modelos[nome_m], nc.campos_do_cliente(banco, c)),
                             height=420, key=f"mt_{c['id']}_{nome_m}")
        b1, b2 = st.columns(2)
        b1.download_button("⬇️ Baixar Word (.docx)", nc.gerar_docx(nome_m, texto), file_name=f"{nome_m} - {c['nome']}.docx",
                           width="stretch", type="primary", key=f"mdl_{c['id']}")
        if b2.button("📎 Guardar cópia na pasta do cliente", width="stretch", key=f"mgu_{c['id']}"):
            nome = f"{HOJE.isoformat()}_{nc.novo_id()[:4]}_{nome_m}.docx"
            nc.guardar_documento(c["id"], nome, nc.gerar_docx(nome_m, texto))
            tipo = "Procuração" if "Procura" in nome_m else ("Contrato de honorários" if "Contrato" in nome_m else "Declaração de hipossuficiência")
            c.setdefault("documentos", []).append({"arquivo": nome, "nome": f"{nome_m}.docx", "tipo": tipo, "data": HOJE.isoformat()})
            salvar("Cópia guardada na pasta (versão para assinatura).")
            st.rerun()
    with t4, st.form(f"dados_{c['id']}"):
        c1, c2, c3 = st.columns(3)
        campos = {}
        for col, (campo, rot) in zip([c1, c2, c3] * 6, [
                ("nome", "Nome"), ("cpf_cnpj", "CPF / CNPJ"), ("rg", "RG"), ("nacionalidade", "Nacionalidade"),
                ("estado_civil", "Estado civil"), ("profissao", "Profissão"), ("telefone", "Telefone / WhatsApp"),
                ("email", "E-mail"), ("valor", "Valor do contrato (R$)")]):
            campos[campo] = col.text_input(rot, c.get(campo, ""))
        campos["endereco"] = st.text_input("Endereço completo (com CEP)", c.get("endereco", ""))
        c1, c2 = st.columns(2)
        segs = cfg.get("segmentos") or ["Outros"]
        campos["segmento"] = c1.selectbox("Segmento", segs, index=segs.index(c["segmento"]) if c.get("segmento") in segs else 0)
        campos["origem"] = c2.selectbox("Como chegou", nc.ORIGENS + ["Processo existente"],
                                        index=(nc.ORIGENS + ["Processo existente"]).index(c["origem"]) if c.get("origem") in nc.ORIGENS + ["Processo existente"] else 0)
        campos["assunto"] = st.text_input("Assunto / objeto do contrato", c.get("assunto", ""))
        campos["honorarios"] = st.text_input("Honorários combinados", c.get("honorarios", ""),
                                             placeholder="ex.: R$ 3.000,00 em 3x + 30% do proveito econômico")
        c1, c2 = st.columns(2)
        campos["proximo_passo"] = c1.text_input("Próximo passo", c.get("proximo_passo", ""))
        dp = c2.date_input("Data do próximo passo", value=nc.para_data(c.get("data_proximo")), format="DD/MM/YYYY")
        campos["obs"] = st.text_area("Anotações (histórico de conversas, combinados)", c.get("obs", ""), height=140)
        if st.form_submit_button("💾 Salvar dados", type="primary"):
            antigo = c["nome"]
            c.update(campos)
            c["data_proximo"] = dp.isoformat() if dp else None
            c["atualizado"] = dt.datetime.now().isoformat(timespec="minutes")
            for p in banco["processos"].values():
                if p.get("cliente_id") == c["id"] or p.get("cliente") == antigo:
                    p["cliente"], p["cliente_id"] = c["nome"], c["id"]
            salvar("Dados salvos.")
            st.rerun()


def pagina_clientes():
    topo()
    st.markdown("### 👥 Clientes")
    pend = lista_clientes(lambda c: c["etapa"] in nc.ETAPAS_ABERTAS)
    fech = lista_clientes(lambda c: c["etapa"] == "Contrato fechado")
    opcoes = {"pend": f"⏳ Pendentes de contrato ({len(pend)})", "fech": f"✅ Contratos fechados ({len(fech)})",
              "pasta": "📂 Pasta do cliente", "novo": "➕ Novo cliente"}
    aba = st.segmented_control("Ver", list(opcoes), format_func=opcoes.get, key="aba_clientes",
                               label_visibility="collapsed") or "pend"
    st.write("")
    busca = nc.sem_acento(st.text_input("Buscar cliente", placeholder="nome, CPF, telefone...", key="busca_cli")) if aba in ("pend", "fech") else ""

    def bate(c):
        return not busca or busca in nc.sem_acento(" ".join(str(c.get(k, "")) for k in ("nome", "cpf_cnpj", "telefone", "assunto")))
    if aba == "pend":
        st.caption("Quem já conversou com você, mas ainda não assinou o contrato. Clique em ✍️ Fechou quando assinar.")
        lista_simples([c for c in pend if bate(c)], "pend", mostrar_fechar=True)
    elif aba == "fech":
        lista_simples([c for c in fech if bate(c)], "fech")
    elif aba == "novo":
        form_novo_contato("cli", "Contrato fechado")
    else:
        todos = lista_clientes()
        if not todos:
            st.info("Nenhum cliente ainda. Cadastre em ➕ Novo cliente ou em 🎯 Prospecção.")
            return
        ids = [c["id"] for c in todos]
        atual = st.session_state.get("cliente_aberto")
        cid = st.selectbox("Cliente", ids, index=ids.index(atual) if atual in ids else 0, key="sel_cliente",
                           format_func=lambda i: f"{banco['clientes'][i]['nome']} · {banco['clientes'][i]['etapa']}")
        st.session_state.cliente_aberto = cid
        pasta_cliente(banco["clientes"][cid])


# ═════════════ Configurações ═════════════
def pagina_config():
    topo()
    st.markdown("### ⚙️ Configurações")
    with st.container(border=True, key="card_cfg1"):
        cabecalho("Escritório")
        c1, c2, c3 = st.columns(3)
        esc_ = c1.text_input("Nome do escritório", cfg.get("escritorio"))
        adv = c2.text_input("Seu nome (aparece nas petições)", cfg.get("advogada"))
        cid = c3.text_input("Cidade (fecho das petições)", cfg.get("cidade"))
        end_esc = st.text_input("Endereço do escritório (vai na procuração e no contrato)", cfg.get("endereco_escritorio", ""))
    with st.container(border=True, key="card_cfg2"):
        cabecalho("Suas OABs (processos de patrocínio)", "principal e suplementares")
        oabs = st.data_editor(pd.DataFrame(cfg.get("oabs") or [], columns=["numero", "uf"]), num_rows="dynamic",
                              key="ed_oabs", width="stretch", hide_index=True,
                              column_config={"numero": st.column_config.TextColumn("Número da OAB", required=True),
                                             "uf": st.column_config.TextColumn("UF", default="PE", max_chars=2)})
        st.caption("Os advogados parceiros ficam na aba 🤝 Parceiros.")
    with st.container(border=True, key="card_cfg3"):
        cabecalho("Busca e prazos")
        c1, c2 = st.columns(2)
        dias = c1.number_input("A cada busca, olhar quantos dias para trás", 1, 60, int(cfg.get("dias_busca") or 7))
        mov = c2.toggle("Contar Carnaval, Quarta/Quinta Santas e Corpus Christi como dias sem prazo",
                        bool(cfg.get("feriados_moveis")),
                        help="Desligado, o app conta esses dias como úteis: o vencimento sai mais cedo (lado seguro).")
        fer = st.text_area("Feriados locais e dias sem expediente (um por linha, dd/mm/aaaa)",
                           "\n".join(nc.br(d) for d in cfg.get("feriados_extras", [])),
                           help="Feriados estaduais, municipais e portarias do tribunal (ex.: TJPE).")
    with st.container(border=True, key="card_cfg4"):
        cabecalho("Segmentos de atuação", "usados na prospecção")
        segs = st.text_area("Um por linha", "\n".join(cfg.get("segmentos") or []), height=200)
    if st.button("💾 Salvar configurações", type="primary"):
        def linhas(df, campos):
            out = []
            for _, l in df.iterrows():
                item = {c: str(l.get(c) or "").strip() for c in campos}
                if nc.so_digitos(item.get("numero")):
                    item["numero"] = nc.so_digitos(item["numero"])
                    item["uf"] = (item.get("uf") or "PE").upper()[:2]
                    out.append(item)
            return out
        datas = [nc.para_data(x.strip()) for x in fer.splitlines() if x.strip()]
        cfg.update({"escritorio": esc_, "advogada": adv, "cidade": cid, "endereco_escritorio": end_esc, "oabs": linhas(oabs, ["numero", "uf"]),
                    "segmentos": [s.strip() for s in segs.splitlines() if s.strip()],
                    "dias_busca": int(dias), "feriados_moveis": mov,
                    "feriados_extras": sorted(d.isoformat() for d in datas if d)})
        salvar("Configurações salvas.")
        st.rerun()
    with st.expander("📋 Histórico das buscas"):
        for b in reversed(banco.get("log_buscas") or []):
            st.markdown(f"**{b['quando'].replace('T', ' ')}** · {b['novas']} nova(s)" + (f" · ⚠️ {' / '.join(b['erros'])}" if b["erros"] else ""))


PAGINA_FN = {"painel": pagina_painel, "intimacoes": pagina_intimacoes, "processos": pagina_processos,
             "prazos": pagina_prazos, "agenda": pagina_agenda, "tarefas": pagina_tarefas, "peticoes": pagina_peticoes,
             "config": pagina_config, "clientes": pagina_clientes, "prospeccao": pagina_prospeccao,
             "parceiros": pagina_parceiros}
PAGINA_FN.get(st.session_state.pagina, pagina_painel)()
