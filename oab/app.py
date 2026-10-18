"""
Dashboard de Estudos · 48º Exame de Ordem (OAB · FGV)
Rodar (dentro da pasta oab):  streamlit run app.py

Fontes de dados (mesma pasta deste arquivo):
- "EDITAL OAB 48.xlsx": edital verticalizado, cronograma semanal e progresso. Toda edição feita no app é gravada nela.
- pasta "base_estudos": resumos e flashcards (.md, um arquivo por matéria), como a FGV cobra e suas anotações.
"""
import base64
import datetime as dt
import json
import re
import shutil
from pathlib import Path

import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from openpyxl import load_workbook

# ───────────────────────── Configuração ─────────────────────────
BASE = Path(__file__).parent
ARQ = BASE / "EDITAL OAB 48.xlsx"
PASTA_BACKUP = BASE / "backup"
PASTA_ESTUDOS = BASE / "base_estudos"
ARQ_ANOTACOES = PASTA_ESTUDOS / "anotacoes.json"
ARQ_BANCA = PASTA_ESTUDOS / "analise_banca.md"
PASTA_MATERIAIS = BASE / "materiais"  # PDFs baixados do curso: ficam só no computador (fora do GitHub)
PERFIL_FGV = ("Múltipla escolha com 4 alternativas (A a D) e o erro não desconta acerto: nunca deixe em branco. "
              "Enunciados longos em forma de caso prático (\"Maria, advogada, ...\"), pedindo a solução "
              "\"de acordo com o CPC/CF/Estatuto\". Cobra muito a letra da lei, súmulas e teses recentes do STF e do STJ. "
              "Leia o comando primeiro e elimine as alternativas absurdas.")
ABA_PAINEL = "Painel e Cronograma"
ABA_REGISTRO = "Registro_Estudos"
ABA_CONFIG = "Config_App"
ABA_PLANO = "Plano_Diario"
ABA_SIMULADOS = "Simulados"
LINHA_CABECALHO = 8
LINHA_INICIAL = 9  # 1ª linha de tópicos em cada aba de matéria
TOTAL_QUESTOES, META_APROVACAO = 80, 40
PROVA_PADRAO = dt.date(2027, 1, 10)       # 1ª fase do 48º Exame (edital FGV)
SEGUNDA_FASE_PADRAO = dt.date(2027, 2, 28)

AZUL, AZUL_CLARO, ESCURO, FUNDO, TEXTO, APAGADO = "#1E1EEB", "#5B6BFF", "#11131F", "#F2F3F8", "#1F2233", "#8B90A5"
AZUL_FUNDO, PRETO_MENU, BORDA = "#EEF0FF", "#0B0B0F", "#E4E6EF"

# Colunas da planilha (posição 1 = coluna A). "% Acerto" (coluna H) é fórmula: o app calcula e nunca grava nela.
COLUNAS = {
    "Cód": 1, "Tópico": 2, "Status": 3, "Data Estudada": 4, "Revisão 7d": 5,
    "Nº Questões": 6, "Acertos": 7, "Observações": 9,
}
COLS_DATA = ["Data Estudada"]
REVISOES = [("Revisão 7d", 7)]
STATUS = ["Não Iniciado", "Em Teoria", "Estudado", "Revisado (7d)", "Concluído"]
OPC_REV = ["Pendente", "Feito", "N/A"]
FEITO = {"Estudado", "Revisado (7d)", "Concluído"}

# Cada matéria (aba da planilha): nome curto, cor, ícone, grupo, questões na prova e meta de acertos
MATERIAS = {
    "Ética Profissional": ("Ética Profissional", "#1E1EEB", "⚖️", "A", 8, 7),
    "Direito Constitucional": ("Dir. Constitucional", "#3B5BFF", "📜", "A", 6, 4),
    "Direito Civil": ("Dir. Civil", "#5B8DEF", "🏠", "A", 6, 4),
    "Processo Civil": ("Processo Civil", "#00A3C4", "📂", "A", 6, 4),
    "Direito Penal": ("Dir. Penal", "#6C4CF5", "🔒", "A", 6, 4),
    "Processo Penal": ("Processo Penal", "#8E7CFF", "🚔", "A", 6, 4),
    "Direito do Trabalho": ("Dir. do Trabalho", "#2E86AB", "👷", "A", 5, 4),
    "Processo do Trabalho": ("Processo do Trabalho", "#4FC3E0", "🏭", "A", 5, 4),
    "Direito Administrativo": ("Dir. Administrativo", "#9B5DE5", "🏛️", "A", 6, 4),
    "Direito Tributário": ("Dir. Tributário", "#14B8A6", "💰", "B", 5, 3),
    "Direito Empresarial": ("Dir. Empresarial", "#7AA2FF", "🏢", "B", 4, 2),
    "Outras Disciplinas OAB": ("Outras disciplinas", "#A3AAC4", "🌐", "B", 18, 9),
}
GRUPOS = {
    "A": {"nome": "Grupo A · Alta relevância", "icone": "🅰️"},
    "B": {"nome": "Grupo B · Média e baixa relevância", "icone": "🅱️"},
}
# Palavras do cronograma semanal que indicam cada matéria (a ordem importa: "Processual Civil" antes de "Civil").
PALAVRAS_MATERIA = [
    ("ética", "Ética Profissional"), ("constitucional", "Direito Constitucional"),
    ("processual civil", "Processo Civil"), ("civil", "Direito Civil"),
    ("processual penal", "Processo Penal"), ("penal", "Direito Penal"),
    ("processual do trabalho", "Processo do Trabalho"), ("trabalho", "Direito do Trabalho"),
    ("administrativo", "Direito Administrativo"), ("tribut", "Direito Tributário"),
    ("empresarial", "Direito Empresarial"), ("societ", "Direito Empresarial"),
]

st.set_page_config(page_title="Avany · OAB 48", page_icon="⚖️", layout="wide")

# Tema claro (branco e azul). No Streamlit Cloud vale o config.toml da raiz do repositório (tema escuro do outro
# dashboard), então o app aplica o tema dele mesmo aqui e recarrega uma vez.
TEMA = {"base": "light", "primaryColor": "#1E1EEB", "backgroundColor": "#F2F3F8",
        "secondaryBackgroundColor": "#FFFFFF", "textColor": "#1F2233"}
if any(st.get_option(f"theme.{k}") != v for k, v in TEMA.items()) and not st.session_state.get("_tema_ok"):
    st.session_state._tema_ok = True
    try:
        for k, v in TEMA.items():
            st._config.set_option(f"theme.{k}", v)
        st.rerun()
    except Exception:
        pass

# ───────────────────────── Estilo branco & azul ─────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, p, label {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: {FUNDO}; color: {TEXTO}; }}
.stApp p, .stApp li, .stApp label, .stApp span {{ color: inherit; }}
h1, h2, h3, h4 {{ font-family: 'Poppins', sans-serif !important; color: {ESCURO} !important; letter-spacing: .2px; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2.2rem; max-width: 1300px; }}
.titulo {{ font-family: 'Poppins', sans-serif; font-size: 1.9rem; font-weight: 700; color: {ESCURO}; margin-bottom: 0; }}
.titulo span {{ color: {AZUL}; }}
.sub {{ color: {APAGADO}; font-size: .95rem; margin-top: -4px; }}
/* Cartões brancos (containers com borda) */
[class*="st-key-card_"] {{ background: #fff; border: 1px solid {BORDA} !important; border-radius: 16px;
  box-shadow: 0 6px 18px rgba(20,24,60,.06); padding: 18px 20px !important; }}
[class*="st-key-card_"] h4 {{ font-size: 1.08rem !important; font-weight: 600 !important; padding: 0 !important; }}
.kpi {{ background: #fff; border: 1px solid {BORDA}; border-radius: 16px; padding: 16px 18px; height: 100%;
  box-shadow: 0 6px 18px rgba(20,24,60,.06); display: flex; gap: 14px; align-items: flex-start; }}
.kpi .ic {{ min-width: 42px; height: 42px; border-radius: 12px; background: {AZUL_FUNDO}; display: flex; align-items: center;
  justify-content: center; font-size: 1.25rem; }}
.kpi .rot {{ color: {APAGADO}; font-size: .74rem; text-transform: uppercase; letter-spacing: 1.1px; }}
.kpi .val {{ color: {ESCURO}; font-family: 'Poppins', sans-serif; font-size: 1.7rem; font-weight: 700; line-height: 1.2; }}
.kpi .det {{ color: {APAGADO}; font-size: .82rem; }}
.kpi.destaque {{ background: {AZUL}; border-color: {AZUL}; box-shadow: 0 10px 24px rgba(30,30,235,.35); }}
.kpi.destaque .rot, .kpi.destaque .det {{ color: #D9DCFF; }}
.kpi.destaque .val {{ color: #fff; }}
.kpi.destaque .ic {{ background: rgba(255,255,255,.18); }}
.barra {{ height: 6px; background: {AZUL_FUNDO}; border-radius: 6px; margin-top: 10px; overflow: hidden; }}
.barra > div {{ height: 100%; background: {AZUL}; border-radius: 6px; }}
.kpi.destaque .barra {{ background: rgba(255,255,255,.25); }}
.kpi.destaque .barra > div {{ background: #fff; }}
.chip {{ display: inline-block; border: 1px solid {BORDA}; border-radius: 999px; padding: 4px 12px; margin: 4px 6px 0 0;
  color: {TEXTO}; font-size: .82rem; background: #fff; }}
.chip b {{ color: {AZUL}; }}
.topo {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 6px; }}
.usuaria {{ display: flex; align-items: center; gap: 10px; background: #fff; border: 1px solid {BORDA}; border-radius: 999px;
  padding: 5px 6px 5px 16px; font-weight: 600; font-size: .85rem; letter-spacing: .8px; color: {ESCURO}; }}
.usuaria .av {{ width: 32px; height: 32px; border-radius: 50%; background: {AZUL}; color: #fff; display: flex;
  align-items: center; justify-content: center; font-family: 'Poppins', sans-serif; }}
.cal {{ display: flex; gap: 8px; justify-content: space-between; margin: 6px 0 4px; }}
.cal div {{ flex: 1; text-align: center; padding: 8px 0; border-radius: 999px; color: {APAGADO}; font-size: .78rem; }}
.cal div b {{ display: block; color: {ESCURO}; font-size: 1.05rem; font-family: 'Poppins', sans-serif; }}
.cal div.hoje {{ background: {AZUL}; color: #D9DCFF; box-shadow: 0 6px 16px rgba(30,30,235,.35); }}
.cal div.hoje b {{ color: #fff; }}
.fonte {{ display: flex; align-items: center; gap: 12px; margin: 9px 0; font-size: .86rem; color: {TEXTO}; }}
.fonte .nome {{ width: 44%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.fonte .trilho {{ flex: 1; height: 5px; background: {AZUL_FUNDO}; border-radius: 6px; overflow: hidden; }}
.fonte .trilho div {{ height: 100%; background: {AZUL}; border-radius: 6px; }}
.fonte .pct {{ width: 40px; text-align: right; color: {APAGADO}; font-size: .8rem; }}
.legenda {{ font-size: .85rem; color: {TEXTO}; line-height: 1.9; }}
.legenda i {{ display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 8px; }}
.resumo {{ background: #fff; border: 1px solid {BORDA}; border-radius: 14px; padding: 18px 22px; color: {TEXTO}; line-height: 1.6; }}
.flash {{ background: #fff; border: 2px solid {AZUL}; border-radius: 18px; box-shadow: 0 8px 22px rgba(30,30,235,.12);
  padding: 34px 28px; text-align: center; font-size: 1.15rem; color: {ESCURO}; min-height: 150px; }}
.flash small {{ display:block; color: {APAGADO}; font-size: .75rem; letter-spacing: 1.4px; text-transform: uppercase; margin-bottom: 12px; }}
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{ border: 1px solid {AZUL}; color: {AZUL};
  background: #fff; border-radius: 10px; }}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{ background: {AZUL}; color: #fff; border-color: {AZUL}; }}
.stButton > button[kind="primary"] {{ background: {AZUL}; color: #fff; border-color: {AZUL}; }}
[data-testid="stSidebar"] {{ background: {PRETO_MENU}; border-right: none; }}
[data-testid="stSidebar"] * {{ color: #E8E9F2; }}
[data-testid="stSidebar"] .stButton > button {{ border: none; background: transparent; justify-content: flex-start;
  text-align: left; color: #E8E9F2; border-radius: 10px; }}
[data-testid="stSidebar"] .stButton > button, [data-testid="stSidebar"] .stButton > button * {{ justify-content: flex-start; text-align: left; }}
[data-testid="stSidebar"] .stButton > button {{ padding-left: 16px; }}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{ background: {AZUL}; color: #fff; }}
[data-testid="stSidebar"] .stButton > button:hover {{ background: #1C1C2B; color: #fff; }}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {{ background: {AZUL}; }}
[data-testid="stSidebar"] [data-testid="stExpander"] {{ border: 1px solid #23233A; border-radius: 12px; background: #121219; }}
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {{ color: #fff; }}
[data-testid="stSidebar"] [data-testid="stExpander"] details, [data-testid="stSidebar"] [data-testid="stExpander"] summary {{
  background: #121219 !important; color: #E8E9F2 !important; }}
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {{ background: #1C1C2B !important; }}
/* Campos do menu (metas e datas): fundo escuro e texto branco, sem nada "apagado" */
[data-testid="stSidebar"] [data-testid="stNumberInputContainer"], [data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="base-input"], [data-testid="stSidebar"] [data-testid="stTextInputRootElement"],
[data-testid="stSidebar"] [data-testid="stDateInput"] > div > div {{ background: #1C1C2B !important; border-color: #2E2E44 !important; }}
[data-testid="stSidebar"] input {{ background: #1C1C2B !important; color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;
  opacity: 1 !important; }}
[data-testid="stSidebar"] [data-testid="stNumberInputContainer"] button {{ background: #1C1C2B !important; color: #E8E9F2 !important; }}
[data-testid="stSidebar"] [data-testid="stNumberInputContainer"] button:hover {{ background: {AZUL} !important; }}
.st-key-menu_metas button[data-testid^="stBaseButton"] {{ border: 1px solid #2E2E44; background: #1C1C2B;
  color: #E8E9F2; justify-content: center; }}
.st-key-menu_metas button[data-testid^="stBaseButton"] * {{ justify-content: center; }}
.st-key-menu_metas button[data-testid^="stBaseButton"]:hover {{ background: {AZUL}; border-color: {AZUL}; }}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{ color: #A3A8BF !important; }}
.logo {{ font-family: 'Poppins', sans-serif; font-size: 1.6rem; font-weight: 700; color: #fff !important; letter-spacing: 1px; }}
.logo span {{ color: {AZUL_CLARO} !important; }}
.logo-sub {{ font-size: .78rem; color: #8B90A5 !important; letter-spacing: 1.2px; text-transform: uppercase; margin-top: -4px; }}
.st-key-busca [data-testid="stTextInputRootElement"] {{ border-radius: 999px; border: 1.5px solid {AZUL}; background: #fff;
  overflow: hidden; }}
.st-key-busca input {{ background: #fff; padding-left: 16px; }}
[data-testid="stExpander"] {{ border: 1px solid {BORDA}; border-radius: 12px; background: #fff; }}
[data-testid="stCheckbox"] label p {{ font-size: .95rem; }}
hr {{ border-color: {BORDA} !important; }}
</style>
""", unsafe_allow_html=True)


# ───────────────────────── Funções auxiliares ─────────────────────────
def vazio(v):
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() == ""
    try:
        return bool(pd.isna(v))
    except (TypeError, ValueError):
        return False


def para_data(v):
    if vazio(v):
        return None
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if isinstance(v, (int, float)):  # número serial do Excel
        return dt.date(1899, 12, 30) + dt.timedelta(days=int(v))
    txt = str(v).strip()[:10]
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return dt.datetime.strptime(txt, fmt).date()
        except ValueError:
            pass
    return None


def para_num(v):
    if vazio(v):
        return 0.0
    try:
        return float(str(v).replace("%", "").replace(",", "."))
    except ValueError:
        return 0.0


def info_materia(aba):
    if aba in MATERIAS:
        return MATERIAS[aba]
    extras = ["#14B8A6", "#4FC3E0", "#7AA2FF", "#9B5DE5"]
    return (aba, extras[sum(map(ord, aba)) % len(extras)], "📘", "B", 0, 0)


def abas_de_materia(wb):
    """Toda aba com 'Cód.' em A8 é tratada como matéria (novas abas entram sozinhas)."""
    return [ws.title for ws in wb.worksheets
            if str(ws.cell(LINHA_CABECALHO, 1).value or "").strip().startswith("Cód")]


def materia_do_texto(txt):
    t = str(txt or "").lower()
    for palavra, aba in PALAVRAS_MATERIA:
        if palavra in t:
            return aba
    return None


# ───────────────────────── Leitura ─────────────────────────
@st.cache_data(show_spinner=False)
def carregar(_mtime):
    wb = load_workbook(ARQ, data_only=True)
    linhas = []
    for aba in abas_de_materia(wb):
        ws = wb[aba]
        nome, cor, emoji, grupo, _, _ = info_materia(aba)
        for r in range(LINHA_INICIAL, ws.max_row + 1):
            cod = ws.cell(r, 1).value
            if vazio(cod):
                continue
            reg = {"id": f"{aba}|{r}", "aba": aba, "linha": r, "Grupo": grupo,
                   "Matéria": f"{emoji} {nome}", "MatériaNome": nome, "Cor": cor}
            for col, idx in COLUNAS.items():
                reg[col] = ws.cell(r, idx).value
            reg["Cód"] = str(reg["Cód"]).strip()
            reg["Tópico"] = str(reg["Tópico"] or "").strip()
            reg["Data Estudada"] = para_data(reg["Data Estudada"])
            reg["Nº Questões"] = int(para_num(reg["Nº Questões"]))
            reg["Acertos"] = min(int(para_num(reg["Acertos"])), reg["Nº Questões"])
            reg["% Acerto"] = round(reg["Acertos"] / reg["Nº Questões"] * 100, 1) if reg["Nº Questões"] else 0.0
            reg["Status"] = reg["Status"] if reg["Status"] in STATUS else "Não Iniciado"
            for c, _ in REVISOES:
                reg[c] = reg[c] if reg[c] in OPC_REV else "Pendente"
            reg["Observações"] = "" if vazio(reg["Observações"]) else str(reg["Observações"])
            linhas.append(reg)
    topicos = pd.DataFrame(linhas).set_index("id")

    registros = pd.DataFrame(columns=["Data", "Matéria", "Cód", "Minutos", "Tipo"])
    if ABA_REGISTRO in wb.sheetnames:
        ws = wb[ABA_REGISTRO]
        dados = [r for r in ws.iter_rows(min_row=2, values_only=True) if r and not vazio(r[0])]
        if dados:
            registros = pd.DataFrame([list(r[:5]) + [None] * (5 - len(r[:5])) for r in dados],
                                     columns=registros.columns)
            registros["Data"] = registros["Data"].map(para_data)
            registros["Minutos"] = registros["Minutos"].map(para_num)
            registros = registros.dropna(subset=["Data"])

    plano_feito = {}
    if ABA_PLANO in wb.sheetnames:
        for d, item, feito in wb[ABA_PLANO].iter_rows(min_row=2, max_col=3, values_only=True):
            if para_data(d) and item:
                plano_feito[(para_data(d), str(item))] = bool(feito)

    simulados = pd.DataFrame(columns=["Data", "Acertos", "Observações"])
    if ABA_SIMULADOS in wb.sheetnames:
        dados = [r for r in wb[ABA_SIMULADOS].iter_rows(min_row=2, max_col=3, values_only=True)
                 if r and para_data(r[0])]
        if dados:
            simulados = pd.DataFrame(dados, columns=simulados.columns)
            simulados["Data"] = simulados["Data"].map(para_data)
            simulados["Acertos"] = simulados["Acertos"].map(lambda v: int(para_num(v)))
            simulados["Observações"] = simulados["Observações"].map(lambda v: "" if vazio(v) else str(v))
            simulados = simulados.sort_values("Data").reset_index(drop=True)

    config = {"meta": 14.0, "inicio": None, "prova": PROVA_PADRAO, "fase2": SEGUNDA_FASE_PADRAO}
    if ABA_CONFIG in wb.sheetnames:
        for chave, valor in wb[ABA_CONFIG].iter_rows(min_row=1, max_col=2, values_only=True):
            if chave == "Meta semanal (h)":
                config["meta"] = para_num(valor) or 14.0
            elif chave == "Início do plano":
                config["inicio"] = para_data(valor)
            elif chave == "Prova 1ª fase":
                config["prova"] = para_data(valor) or PROVA_PADRAO
            elif chave == "Prova 2ª fase":
                config["fase2"] = para_data(valor) or SEGUNDA_FASE_PADRAO
    if config["inicio"] is None:
        datas = list(registros["Data"]) + [d for d in topicos["Data Estudada"] if d]
        config["inicio"] = min(datas) if datas else dt.date.today()
    return topicos, registros, plano_feito, simulados, config


@st.cache_data(show_spinner=False)
def plano_semanal(_mtime):
    """Lê o 'Cronograma semanal estruturado' da aba Painel e Cronograma."""
    try:
        wb = load_workbook(ARQ, data_only=True)
    except Exception:
        return {}
    if ABA_PAINEL not in wb.sheetnames:
        return {}
    grade, cab = {}, None
    for row in wb[ABA_PAINEL].iter_rows(values_only=True):
        if row and str(row[0] or "").strip() == "Dia da Semana":
            cab = [str(c or "") for c in row]
            continue
        if cab and row and row[0] and str(row[0]).strip().endswith(("-feira", "Sábado", "Domingo")):
            grade[str(row[0]).strip()] = dict(zip(cab, row))
    return grade


@st.cache_data(show_spinner=False)
def carregar_base(_assinatura):
    """Lê base_estudos/*.md. Formato: '## CÓD', '### Resumo', '### Flashcards' com linhas 'P:' e 'R:'."""
    base = {}
    for arq in sorted(PASTA_ESTUDOS.glob("*.md")):
        if arq.name == ARQ_BANCA.name:
            continue
        texto = arq.read_text(encoding="utf-8")
        for bloco in re.split(r"^## ", texto, flags=re.M)[1:]:
            cod, _, corpo = bloco.partition("\n")
            resumo, _, cartas = corpo.partition("### Flashcards")
            resumo = re.sub(r"^### Resumo\s*", "", resumo.strip()).strip()
            flash = re.findall(r"^\s*-?\s*P:\s*(.+?)\s*\n\s*R:\s*(.+?)\s*$", cartas, flags=re.M)
            base[cod.strip()] = {"resumo": resumo, "flashcards": flash}
    return base


@st.cache_data(show_spinner=False)
def carregar_banca(_mtime):
    """Lê base_estudos/analise_banca.md: '## CÓD' + linhas 'Palavras-chave:' e 'FGV:'."""
    if not ARQ_BANCA.exists():
        return {}
    dados = {}
    for bloco in re.split(r"^## ", ARQ_BANCA.read_text(encoding="utf-8"), flags=re.M)[1:]:
        cod, _, corpo = bloco.partition("\n")
        item = {"palavras": [], "FGV": ""}
        for linha in corpo.splitlines():
            chave, sep, valor = linha.partition(":")
            if not sep:
                continue
            if chave.strip() == "Palavras-chave":
                item["palavras"] = [p.strip() for p in valor.split(";") if p.strip()]
            elif chave.strip() == "FGV":
                item["FGV"] = valor.strip()
        dados[cod.strip()] = item
    return dados


def pontos_do_resumo(resumo):
    """Cada tópico (linha com '-') do resumo vira um ponto para anotar."""
    return [l.strip()[2:].strip() for l in resumo.splitlines() if l.strip().startswith("- ")]


def ler_anotacoes():
    try:
        return json.loads(ARQ_ANOTACOES.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# ───────────────────────── Sincronização com o GitHub (versão online) ─────────────────────────
# Online (Streamlit Cloud) os arquivos do servidor são apagados quando o app reinicia. Por isso, se houver
# um token em Secrets ([github] token = "..."), a planilha e as anotações são lidas e gravadas no branch
# "dados" do repositório, dentro da pasta "oab". Sem token (no computador), nada disso acontece.
def config_github():
    try:
        cfg = st.secrets["github"]
        return {"token": cfg["token"], "repo": cfg.get("repo", "cristielesilva/dashboard-estudos"),
                "branch": cfg.get("branch", "dados"), "pasta": cfg.get("pasta", "oab").strip("/")}
    except Exception:
        return None


def caminho_no_repo(cfg, arq):
    rel = arq.relative_to(BASE).as_posix()
    return f"{cfg['pasta']}/{rel}" if cfg["pasta"] else rel


def _api(cfg, metodo, caminho, **kw):
    cab = {"Authorization": f"Bearer {cfg['token']}", "Accept": "application/vnd.github+json"}
    cab.update(kw.pop("headers", {}))
    url = f"https://api.github.com/repos/{cfg['repo']}" + (f"/{caminho}" if caminho else "")
    return requests.request(metodo, url,
                            headers=cab, timeout=20, **kw)


class ErroGitHub(Exception):
    pass


def _garantir_branch(cfg):
    repo = _api(cfg, "GET", "")
    if repo.status_code in (401, 403, 404):
        raise ErroGitHub(
            f"O GitHub recusou a chave (código {repo.status_code}). Confira em Settings > Secrets se o token "
            f"foi colado inteiro, entre aspas, e se ele tem acesso ao repositório {cfg['repo']} "
            "com a permissão Contents em Read and write.")
    if _api(cfg, "GET", f"branches/{cfg['branch']}").status_code == 200:
        return
    padrao = repo.json().get("default_branch", "main")
    ref = _api(cfg, "GET", f"git/ref/heads/{padrao}")
    criar = None
    if ref.status_code == 200:
        criar = _api(cfg, "POST", "git/refs",
                     json={"ref": f"refs/heads/{cfg['branch']}", "sha": ref.json()["object"]["sha"]})
    if criar is None or criar.status_code not in (201, 422):
        raise ErroGitHub(
            f"Não consegui criar o branch \"{cfg['branch']}\" no GitHub. Verifique se o token tem a "
            "permissão Contents em Read and write.")


@st.cache_resource(show_spinner="Carregando seus dados salvos...")
def baixar_do_github():
    """Roda uma vez quando o servidor liga: traz a versão mais recente dos dados."""
    cfg = config_github()
    if not cfg:
        return None
    try:
        _garantir_branch(cfg)
    except (ErroGitHub, requests.RequestException) as erro:
        return str(erro)
    for arq in (ARQ, ARQ_ANOTACOES):
        r = _api(cfg, "GET", f"contents/{caminho_no_repo(cfg, arq)}", params={"ref": cfg["branch"]},
                 headers={"Accept": "application/vnd.github.raw"})
        if r.status_code == 200:
            arq.parent.mkdir(exist_ok=True)
            arq.write_bytes(r.content)
    return None


def enviar_ao_github(arq):
    cfg = config_github()
    if not cfg:
        return
    rel = caminho_no_repo(cfg, arq)
    try:
        atual = _api(cfg, "GET", f"contents/{rel}", params={"ref": cfg["branch"]})
        corpo = {"message": f"Atualiza {arq.name} pelo dashboard OAB", "branch": cfg["branch"],
                 "content": base64.b64encode(arq.read_bytes()).decode()}
        if atual.status_code == 200:
            corpo["sha"] = atual.json()["sha"]
        r = _api(cfg, "PUT", f"contents/{rel}", json=corpo)
        r.raise_for_status()
    except Exception as erro:
        st.warning(f"Salvo no app, mas não consegui enviar ao GitHub ({erro}). Confira o token em Secrets.")


# ───────────────────────── Gravação ─────────────────────────
def fazer_backup():
    if st.session_state.get("backup_feito"):
        return
    PASTA_BACKUP.mkdir(exist_ok=True)
    carimbo = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(ARQ, PASTA_BACKUP / f"{ARQ.stem}_{carimbo}.xlsx")
    for velho in sorted(PASTA_BACKUP.glob(f"{ARQ.stem}_*.xlsx"))[:-10]:  # guarda os 10 últimos
        velho.unlink(missing_ok=True)
    st.session_state.backup_feito = True


def salvar(alteracoes=(), novos_registros=(), config=None, plano=None, simulado=None):
    """alteracoes: lista de (id, coluna, valor). Grava tudo de uma vez na planilha original."""
    try:
        fazer_backup()
        wb = load_workbook(ARQ)
        for ident, col, valor in alteracoes:
            aba, linha = ident.rsplit("|", 1)
            cel = wb[aba].cell(int(linha), COLUNAS[col])
            if col in COLS_DATA:
                cel.value = valor
                if valor:
                    cel.number_format = "DD/MM/YYYY"
            elif col in ("Nº Questões", "Acertos"):
                cel.value = int(valor or 0)
            else:
                cel.value = valor
        if novos_registros:
            if ABA_REGISTRO not in wb.sheetnames:
                wb.create_sheet(ABA_REGISTRO).append(["Data", "Matéria", "Cód", "Minutos", "Tipo"])
            ws = wb[ABA_REGISTRO]
            for reg in novos_registros:
                ws.append(reg)
                ws.cell(ws.max_row, 1).number_format = "DD/MM/YYYY"
        if plano:
            data, item, feito = plano
            if ABA_PLANO not in wb.sheetnames:
                wb.create_sheet(ABA_PLANO).append(["Data", "Item do plano", "Feito"])
            ws = wb[ABA_PLANO]
            for r in range(2, ws.max_row + 1):
                if para_data(ws.cell(r, 1).value) == data and ws.cell(r, 2).value == item:
                    ws.cell(r, 3).value = feito
                    break
            else:
                ws.append([data, item, feito])
                ws.cell(ws.max_row, 1).number_format = "DD/MM/YYYY"
        if simulado:
            if ABA_SIMULADOS not in wb.sheetnames:
                wb.create_sheet(ABA_SIMULADOS).append(["Data", f"Acertos (de {TOTAL_QUESTOES})", "Observações"])
            ws = wb[ABA_SIMULADOS]
            ws.append(list(simulado))
            ws.cell(ws.max_row, 1).number_format = "DD/MM/YYYY"
        if config:
            if ABA_CONFIG in wb.sheetnames:
                del wb[ABA_CONFIG]
            ws = wb.create_sheet(ABA_CONFIG)
            ws.append(["Meta semanal (h)", config["meta"]])
            ws.append(["Início do plano", config["inicio"]])
            ws.append(["Prova 1ª fase", config["prova"]])
            ws.append(["Prova 2ª fase", config["fase2"]])
            for r in (2, 3, 4):
                ws.cell(r, 2).number_format = "DD/MM/YYYY"
        wb.save(ARQ)
        enviar_ao_github(ARQ)
    except PermissionError:
        st.error("⚠️ Não consegui salvar: a planilha está aberta no Excel. Feche o arquivo e repita a alteração.")
        return False
    st.cache_data.clear()
    st.session_state.versao = st.session_state.get("versao", 0) + 1
    st.session_state.ultimo_salvo = dt.datetime.now().strftime("%H:%M:%S")
    return True


def salvar_anotacao(cod, texto=None, links=None, pdfs=None):
    """Grava só os campos informados, mantendo os demais."""
    PASTA_ESTUDOS.mkdir(exist_ok=True)
    todas = ler_anotacoes()
    nota = todas.get(cod, {})
    for campo, valor in (("texto", texto), ("links", links), ("pdfs", pdfs)):
        if valor is not None:
            nota[campo] = valor
    nota["atualizado"] = dt.date.today().isoformat()
    todas[cod] = nota
    ARQ_ANOTACOES.write_text(json.dumps(todas, ensure_ascii=False, indent=2), encoding="utf-8")
    enviar_ao_github(ARQ_ANOTACOES)


# ───────────────────────── Componentes visuais ─────────────────────────
def kpi(rotulo, valor, detalhe="", progresso=None, icone="📌", destaque=False):
    barra = ""
    if progresso is not None:
        p = max(0, min(100, progresso))
        barra = f'<div class="barra"><div style="width:{p:.0f}%"></div></div>'
    st.markdown(f'<div class="kpi{" destaque" if destaque else ""}"><div class="ic">{icone}</div>'
                f'<div style="flex:1"><div class="rot">{rotulo}</div><div class="val">{valor}</div>'
                f'<div class="det">{detalhe}</div>{barra}</div></div>', unsafe_allow_html=True)


def estilo(fig, altura=330, titulo=None):
    fig.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=TEXTO, family="Inter"), height=altura, showlegend=False,
                      margin=dict(l=10, r=20, t=50 if titulo else 10, b=10),
                      title=dict(text=titulo, font=dict(color=ESCURO, size=16, family="Poppins")))
    fig.update_xaxes(gridcolor="#ECEEF5", zerolinecolor="#ECEEF5", linecolor=BORDA)
    fig.update_yaxes(gridcolor="#ECEEF5", zerolinecolor="#ECEEF5", linecolor=BORDA)
    return fig


def cores(df):
    return dict(zip(df["Matéria"], df["Cor"]))


def taxa_acerto(df):
    q = df["Nº Questões"].sum()
    return df["Acertos"].sum() / q * 100 if q else 0.0


def fmt_p(p):
    return f"{p:.1f}%".replace(".", ",")


def fmt_h(h):
    return f"{h:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".") + " h"


def avisar(msg, icone):
    """Guarda o aviso para mostrar depois do recarregamento da página."""
    st.session_state.aviso = (msg, icone)


def ir(pagina, **extra):
    st.session_state.pagina = pagina
    st.session_state.update(extra)


def resumo_materias(df):
    g = df.groupby(["Matéria", "Cor", "aba"], sort=False).agg(
        total=("Status", "size"), feitos=("Status", lambda s: s.isin(FEITO).sum()),
        questoes=("Nº Questões", "sum"), acertos=("Acertos", "sum")).reset_index()
    g["% Concluído"] = (g["feitos"] / g["total"] * 100).round(1)
    g["% Acerto"] = [round(a / q * 100, 1) if q else 0.0 for a, q in zip(g["acertos"], g["questoes"])]
    g["Na prova"] = [info_materia(a)[4] for a in g["aba"]]
    return g


def revisoes_pendentes(df, ate):
    linhas = []
    for ident, r in df.iterrows():
        base = r["Data Estudada"]
        if not base:
            continue
        for col, dias in REVISOES:
            if r[col] == "Pendente":
                venc = base + dt.timedelta(days=dias)
                if venc <= ate:
                    linhas.append({"id": ident, "Coluna": col, "Matéria": r["Matéria"], "Cód": r["Cód"],
                                   "Tópico": r["Tópico"], "Revisão": col, "Vence em": venc,
                                   "Atraso (dias)": (dt.date.today() - venc).days})
    return pd.DataFrame(linhas)


def proximo_topico(aba):
    """Primeiro tópico ainda não estudado da matéria (para o Plano de hoje)."""
    sub = topicos[(topicos["aba"] == aba) & ~topicos["Status"].isin(FEITO)]
    return sub.index[0] if len(sub) else None


# ───────────────────────── Tabela editável (salva automaticamente) ─────────────────────────
ORDEM = ["Status", "Matéria", "Cód", "Tópico", "Data Estudada", "Nº Questões", "Acertos", "% Acerto",
         "Revisão 7d", "Observações"]
EDITAVEIS = ["Status", "Data Estudada", "Nº Questões", "Acertos", "Revisão 7d", "Observações"]


def normalizar(col, v):
    if col in COLS_DATA:
        return para_data(v)
    if col in ("Nº Questões", "Acertos"):
        return max(0, int(para_num(v)))
    return "" if vazio(v) else str(v)


def tabela_editavel(df, chave):
    vis = df[ORDEM].copy()
    for c in COLS_DATA:
        vis[c] = pd.to_datetime(vis[c])
    cfg = {
        "Status": st.column_config.SelectboxColumn("Status", options=STATUS, required=True, width="small"),
        "Matéria": st.column_config.TextColumn("Matéria", width="medium"),
        "Cód": st.column_config.TextColumn("Cód", width="small"),
        "Tópico": st.column_config.TextColumn("Tópico", width="large"),
        "Data Estudada": st.column_config.DateColumn("Estudado em", format="DD/MM/YYYY"),
        "Nº Questões": st.column_config.NumberColumn("Questões", min_value=0, step=1),
        "Acertos": st.column_config.NumberColumn("Acertos", min_value=0, step=1),
        "% Acerto": st.column_config.NumberColumn("% Acerto", format="%.0f%%", help="Calculado: acertos ÷ questões"),
        "Revisão 7d": st.column_config.SelectboxColumn("Revisão 7d", options=OPC_REV, width="small"),
        "Observações": st.column_config.TextColumn("Anotações / pontos-chave", width="medium"),
    }
    editado = st.data_editor(
        vis, key=f"{chave}_v{st.session_state.get('versao', 0)}", column_config=cfg, hide_index=True,
        width="stretch", height=min(38 * len(vis) + 40, 620),
        disabled=[c for c in ORDEM if c not in EDITAVEIS])

    alteracoes = []
    for ident in vis.index:
        for col in EDITAVEIS:
            antes, depois = normalizar(col, df.at[ident, col]), normalizar(col, editado.at[ident, col])
            if col == "Acertos":  # não deixa ter mais acertos do que questões
                depois = min(depois, normalizar("Nº Questões", editado.at[ident, "Nº Questões"]))
            if antes != depois:
                alteracoes.append((ident, col, depois))
                # Estudou e não marcou a data? Preenche com hoje para a revisão de 7 dias começar a contar.
                if col == "Status" and depois in FEITO and not df.at[ident, "Data Estudada"] \
                        and not normalizar("Data Estudada", editado.at[ident, "Data Estudada"]):
                    alteracoes.append((ident, "Data Estudada", dt.date.today()))
    if alteracoes and salvar(alteracoes):
        avisar(f"Salvo na planilha ✓ ({len(alteracoes)} alteração(ões))", "💾")
        st.rerun()


# ───────────────────────── Pomodoro (HTML/JS) ─────────────────────────
POMODORO_HTML = f"""
<div id="p" style="font-family:Inter,sans-serif;color:{TEXTO};text-align:center;padding:4px">
  <div style="display:flex;gap:8px;justify-content:center;margin-bottom:8px">
    <button class="m" data-m="25">Foco 25</button><button class="m" data-m="5">Pausa 5</button><button class="m" data-m="15">Pausa 15</button>
  </div>
  <svg width="200" height="200" viewBox="0 0 230 230">
    <circle cx="115" cy="115" r="100" stroke="{AZUL_FUNDO}" stroke-width="12" fill="none"/>
    <circle id="arc" cx="115" cy="115" r="100" stroke="{AZUL}" stroke-width="12" fill="none" stroke-linecap="round"
      transform="rotate(-90 115 115)" stroke-dasharray="628.3" stroke-dashoffset="0"/>
    <text id="t" x="115" y="125" text-anchor="middle" font-size="46" fill="{ESCURO}" font-family="Poppins,sans-serif" font-weight="700">25:00</text>
    <text id="lbl" x="115" y="155" text-anchor="middle" font-size="13" fill="{APAGADO}">FOCO</text>
  </svg>
  <div style="display:flex;gap:10px;justify-content:center;margin-top:6px">
    <button id="go" class="b">▶ Iniciar</button><button id="rs" class="b">↺ Zerar</button>
  </div>
  <div id="msg" style="margin-top:8px;font-size:.85rem;color:{APAGADO}">Ciclos de foco nesta sessão: 0</div>
</div>
<style>
 button{{background:#fff;border:1px solid {AZUL};color:{AZUL};border-radius:10px;padding:6px 14px;cursor:pointer;font-size:.9rem}}
 button:hover,button.on{{background:{AZUL};color:#fff}}
</style>
<script>
const K='pomodoro_oab_v1', C=628.3;
let s={{modo:25,rest:1500,rodando:false,fim:null,ciclos:0}}, ctx=null;
try{{const x=JSON.parse(localStorage.getItem(K)); if(x) s=x;}}catch(e){{}}
const $=id=>document.getElementById(id);
function grava(){{try{{localStorage.setItem(K,JSON.stringify(s));}}catch(e){{}}}}
function bip(){{try{{ctx=ctx||new AudioContext();[0,0.35,0.7].forEach(d=>{{const o=ctx.createOscillator(),g=ctx.createGain();
 o.frequency.value=880;o.connect(g);g.connect(ctx.destination);g.gain.setValueAtTime(.25,ctx.currentTime+d);
 g.gain.exponentialRampToValueAtTime(.001,ctx.currentTime+d+.3);o.start(ctx.currentTime+d);o.stop(ctx.currentTime+d+.3);}});}}catch(e){{}}}}
function modo(m){{s.modo=m;s.rest=m*60;s.rodando=false;s.fim=null;grava();desenha();}}
function desenha(){{
  const m=Math.floor(s.rest/60),sg=Math.floor(s.rest%60);
  $('t').textContent=String(m).padStart(2,'0')+':'+String(sg).padStart(2,'0');
  $('arc').style.strokeDashoffset=C*(1-s.rest/(s.modo*60));
  $('lbl').textContent=s.modo==25?'FOCO':'PAUSA';
  $('go').textContent=s.rodando?'❚❚ Pausar':'▶ Iniciar';
  document.querySelectorAll('.m').forEach(b=>b.classList.toggle('on',+b.dataset.m==s.modo));
  $('msg').textContent='Ciclos de foco nesta sessão: '+s.ciclos;
}}
setInterval(()=>{{ if(!s.rodando) return;
  s.rest=Math.max(0,(s.fim-Date.now())/1000);
  if(s.rest<=0){{ s.rodando=false; bip();
    if(s.modo==25){{s.ciclos++; const longa=s.ciclos%4==0; s.modo=longa?15:5; s.rest=s.modo*60;
      $('msg').textContent='Pomodoro concluído! Registre abaixo.';}}
    else {{ s.modo=25; s.rest=1500; }}
    grava(); desenha(); return; }}
  desenha(); }}, 250);
$('go').onclick=()=>{{ try{{ctx=ctx||new AudioContext();}}catch(e){{}}
  if(s.rodando){{s.rodando=false;}} else {{s.rodando=true;s.fim=Date.now()+s.rest*1000;}} grava();desenha(); }};
$('rs').onclick=()=>modo(s.modo);
document.querySelectorAll('.m').forEach(b=>b.onclick=()=>modo(+b.dataset.m));
desenha();
</script>
"""


def pomodoro():
    if hasattr(st, "iframe"):
        st.iframe(POMODORO_HTML, height=320)
    else:
        components.html(POMODORO_HTML, height=320)


def registrar_estudo(topicos, chave, cod_fixo=None):
    """Botões para lançar um pomodoro (25 min) ou minutos avulsos numa matéria/tópico."""
    if cod_fixo:
        linha = topicos[topicos["Cód"] == cod_fixo].iloc[0]
        nome_mat, cod, ident = linha["MatériaNome"], cod_fixo, topicos.index[topicos["Cód"] == cod_fixo][0]
    else:
        mats = list(dict.fromkeys(topicos["Matéria"]))
        mat = st.selectbox("Matéria estudada", mats, key=f"{chave}_mat")
        sub = topicos[topicos["Matéria"] == mat]
        opcoes = ["— sem tópico específico —"] + [f"{r['Cód']} · {str(r['Tópico'])[:60]}" for _, r in sub.iterrows()]
        top = st.selectbox("Tópico", opcoes, key=f"{chave}_top")
        nome_mat = sub["MatériaNome"].iloc[0]
        cod = "" if top.startswith("—") else top.split(" · ")[0]
        ident = sub.index[sub["Cód"] == cod][0] if cod else None
    b1, b2, b3 = st.columns([1.4, .8, 1])
    reg_pomo = b1.button("✅ Pomodoro 25 min", key=f"{chave}_pomo", width="stretch")
    minutos = b2.number_input("min", 5, 600, 60, 5, key=f"{chave}_min", label_visibility="collapsed")
    reg_man = b3.button(f"➕ {minutos} min", key=f"{chave}_man", width="stretch")
    if reg_pomo or reg_man:
        mins, tipo = (25, "Pomodoro") if reg_pomo else (minutos, "Manual")
        alt = []
        if ident and topicos.at[ident, "Status"] == "Não Iniciado":
            alt.append((ident, "Status", "Em Teoria"))
        if salvar(alt, [[dt.date.today(), nome_mat, cod, mins, tipo]]):
            avisar(f"{mins} min registrados em {nome_mat} ✓", "⏱️")
            st.rerun()


# ───────────────────────── Dados ─────────────────────────
erro_sync = baixar_do_github()
if erro_sync:
    st.warning(f"⚠️ Suas edições não estão sendo salvas online. {erro_sync}")
if not ARQ.exists():
    st.error(f"Não encontrei a planilha **{ARQ.name}** na pasta {BASE}. Coloque o app.py na mesma pasta dela.")
    st.stop()

topicos, registros, plano_feito, simulados, config = carregar(ARQ.stat().st_mtime)
grade = plano_semanal(ARQ.stat().st_mtime)
banca = carregar_banca(ARQ_BANCA.stat().st_mtime if ARQ_BANCA.exists() else 0)
base_estudos = carregar_base(tuple(f.stat().st_mtime for f in sorted(PASTA_ESTUDOS.glob("*.md"))))
hoje = dt.date.today()
st.session_state.setdefault("pagina", "inicio")
pagina = st.session_state.pagina

if "aviso" in st.session_state:
    _msg, _ic = st.session_state.pop("aviso")
    st.toast(_msg, icon=_ic)

# ───────────────────────── Menu lateral ─────────────────────────
with st.sidebar:
    st.markdown("<div class='logo'>AVANY<span>.</span></div><div class='logo-sub'>Rumo à OAB · 48º Exame</div>",
                unsafe_allow_html=True)
    st.write("")
    st.button("🏠 Início", on_click=ir, args=("inicio",), width="stretch",
              type="primary" if pagina == "inicio" else "secondary")
    st.button("📚 Estudar", on_click=ir, args=("estudar",), width="stretch",
              type="primary" if pagina == "estudar" else "secondary")
    st.button("📝 Resumo do dia", on_click=ir, args=("resumo_dia",), width="stretch",
              type="primary" if pagina == "resumo_dia" else "secondary")
    n_rev = len(revisoes_pendentes(topicos, hoje))
    st.button(f"🔁 Revisões ({n_rev})", on_click=ir, args=("revisoes",), width="stretch",
              type="primary" if pagina == "revisoes" else "secondary")
    st.button("🧪 Simulados", on_click=ir, args=("simulados",), width="stretch",
              type="primary" if pagina == "simulados" else "secondary")
    st.write("")
    for chave, grp in GRUPOS.items():
        df_g = topicos[topicos["Grupo"] == chave]
        pct = df_g["Status"].isin(FEITO).mean() * 100 if len(df_g) else 0
        ativo = pagina == f"grupo:{chave}"
        with st.expander(f"{grp['icone']} Grupo {chave} · {pct:.0f}%", expanded=ativo):
            mat_ativa = st.session_state.get("materia_sel") if ativo else None
            st.button("📋 Todas as matérias", key=f"nav_{chave}_todas", width="stretch",
                      on_click=ir, args=(f"grupo:{chave}",), kwargs={"materia_sel": None},
                      type="primary" if ativo and not mat_ativa else "secondary")
            for mat, g in df_g.groupby("Matéria", sort=False):
                p = g["Status"].isin(FEITO).mean() * 100
                st.button(f"{mat} · {p:.0f}%", key=f"nav_{chave}_{mat}", width="stretch",
                          on_click=ir, args=(f"grupo:{chave}",), kwargs={"materia_sel": mat},
                          type="primary" if ativo and mat_ativa == mat else "secondary")
    st.write("")
    with st.container(key="menu_metas"), st.expander("⚙️ Metas e arquivo"):
        meta = st.number_input("Meta semanal de horas", 1.0, 80.0, float(config["meta"]), 0.5, format="%.1f",
                               help="O plano da planilha: 2h por dia, de segunda a domingo (simulado no domingo).")
        inicio = st.date_input("Início do plano", config["inicio"], format="DD/MM/YYYY")
        prova = st.date_input("Prova da 1ª fase", config["prova"], format="DD/MM/YYYY")
        fase2 = st.date_input("Prova da 2ª fase", config["fase2"], format="DD/MM/YYYY")
        novo = {"meta": meta, "inicio": inicio, "prova": prova, "fase2": fase2}
        if any(novo[k] != config[k] for k in novo):
            if st.button("Salvar metas", width="stretch"):
                if salvar(config=novo):
                    st.rerun()
        st.caption(f"💾 Último salvamento: {st.session_state.get('ultimo_salvo', '—')}")
        if st.button("🔄 Recarregar planilha", width="stretch",
                     help="Use depois de editar a planilha direto no Excel."):
            st.cache_data.clear()
            st.session_state.versao = st.session_state.get("versao", 0) + 1
            st.rerun()
        st.caption("Feche a planilha no Excel enquanto usa o app, senão o salvamento é bloqueado.")


# ═════════════ Barra do topo: busca + usuária ═════════════
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
         "novembro", "dezembro"]
CORES_STATUS = {"Não Iniciado": "#D9DCF5", "Em Teoria": "#9AA4FF", "Estudado": "#5B6BFF",
                "Revisado (7d)": "#2F3CF0", "Concluído": "#10129A"}


def barra_topo():
    c1, c2 = st.columns([3, 1], vertical_alignment="center")
    busca = c1.text_input("Buscar", placeholder="🔍  Buscar tópico, código ou matéria (ex.: honorários, ETI.04)",
                          key="busca", label_visibility="collapsed")
    c2.markdown("<div style='display:flex;justify-content:flex-end'><div class='usuaria'>AVANY"
                "<div class='av'>A</div></div></div>", unsafe_allow_html=True)
    termo = busca.strip().lower()
    if len(termo) >= 2:
        alvo = (topicos["Tópico"].astype(str) + " " + topicos["Cód"].astype(str) + " " + topicos["Matéria"]).str.lower()
        achados = topicos[alvo.str.contains(re.escape(termo))].head(8)
        with st.container(border=True, key="card_1"):
            if achados.empty:
                st.caption("Nenhum tópico encontrado.")
            for ident, r in achados.iterrows():
                st.button(f"{r['Cód']} · {str(r['Tópico'])[:80]} · {r['Matéria']} · {r['Status']}",
                          key=f"busca_{ident}", on_click=ir, args=("estudar",),
                          kwargs={"estudo_id": ident, "busca": ""})


def cartao_titulo(texto, detalhe=""):
    st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:baseline'>"
                f"<h4 style='margin:0 0 4px'>{texto}</h4><span style='color:{APAGADO};font-size:.82rem'>{detalhe}</span>"
                f"</div>", unsafe_allow_html=True)


# ═════════════ Página: Início ═════════════
def pagina_inicio():
    st.markdown('<div class="titulo">Bom estudo, <span>Avany</span></div>', unsafe_allow_html=True)
    st.markdown(f'<span class="chip">⚖️ 1ª fase · <b>{(prova - hoje).days} dias</b> ({prova:%d/%m/%Y})</span>'
                f'<span class="chip">✍️ 2ª fase · <b>{(fase2 - hoje).days} dias</b> ({fase2:%d/%m/%Y})</span>'
                f'<span class="chip">🎯 Meta <b>{META_APROVACAO} de {TOTAL_QUESTOES}</b> acertos</span>'
                f'<span class="chip">Banca <b>FGV</b></span>', unsafe_allow_html=True)
    st.write("")

    horas = registros["Minutos"].sum() / 60 if len(registros) else 0.0
    planejadas = meta / 7 * max(1, (hoje - inicio).days + 1)
    feitos = topicos["Status"].isin(FEITO).sum()
    pct = feitos / len(topicos) * 100 if len(topicos) else 0
    acerto = taxa_acerto(topicos)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi("Edital estudado", fmt_p(pct), f"{feitos} de {len(topicos)} tópicos", pct, "📚", destaque=True)
    with k2:
        kpi("Horas estudadas", fmt_h(horas), f"de {fmt_h(planejadas)} planejadas até hoje",
            horas / planejadas * 100 if planejadas else 0, "⏱️")
    with k3:
        kpi("Taxa de acertos", fmt_p(acerto), f"{int(topicos['Nº Questões'].sum())} questões · meta 50%", acerto, "🎯")
    with k4:
        if len(simulados):
            ult = simulados.iloc[-1]
            kpi("Último simulado", f"{ult['Acertos']}/{TOTAL_QUESTOES}",
                "✅ acima da meta" if ult["Acertos"] >= META_APROVACAO
                else f"faltam {META_APROVACAO - ult['Acertos']} para os {META_APROVACAO}",
                ult["Acertos"] / TOTAL_QUESTOES * 100, "🧪")
        else:
            kpi("Último simulado", "—", "registre o simulado de domingo", None, "🧪")
    st.write("")

    # Linha 1: horas por dia (área azul) + situação do edital (rosca)
    g1, g2 = st.columns([1.75, 1], gap="medium")
    with g1, st.container(border=True, key="card_2"):
        dias30 = pd.date_range(hoje - dt.timedelta(days=29), hoje).date
        por_dia = registros.groupby("Data")["Minutos"].sum() / 60 if len(registros) else pd.Series(dtype=float)
        serie = pd.DataFrame({"Dia": dias30, "Horas": [round(por_dia.get(d, 0.0), 2) for d in dias30]})
        cartao_titulo("Horas de estudo", f"últimos 30 dias · total {fmt_h(serie['Horas'].sum())}")
        fig = go.Figure(go.Scatter(
            x=serie["Dia"], y=serie["Horas"], mode="lines", line=dict(color=AZUL, width=3, shape="spline"),
            fill="tozeroy", fillgradient=dict(type="vertical", colorscale=[[0, "rgba(30,30,235,0.02)"],
                                                                           [1, "rgba(30,30,235,0.45)"]]),
            hovertemplate="%{x|%d/%m}: %{y:.1f} h<extra></extra>"))
        fig.add_hline(y=meta / 7, line_dash="dot", line_color=APAGADO,
                      annotation_text=f"meta diária {meta / 7:.1f}h", annotation_font_color=APAGADO)
        fig.update_xaxes(tickformat="%d/%m", showgrid=False)
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(estilo(fig, 300), width="stretch")
    with g2, st.container(border=True, key="card_3"):
        cartao_titulo("Situação do edital", f"{len(topicos)} tópicos")
        cont = topicos["Status"].value_counts().reindex(STATUS, fill_value=0)
        fig = go.Figure(go.Pie(labels=cont.index, values=cont.values, hole=.68, sort=False,
                               marker=dict(colors=[CORES_STATUS[k] for k in cont.index]),
                               textinfo="none", hovertemplate="%{label}: %{value}<extra></extra>"))
        fig.add_annotation(text=f"<b>{fmt_p(pct)}</b><br><span style='font-size:11px'>estudado</span>",
                           showarrow=False, font=dict(size=20, color=ESCURO, family="Poppins"))
        st.plotly_chart(estilo(fig, 200), width="stretch")
        st.markdown("<div class='legenda'>" + "".join(
            f"<div><i style='background:{CORES_STATUS[k]}'></i>{k} <b style='float:right'>{v}</b></div>"
            for k, v in cont.items()) + "</div>", unsafe_allow_html=True)
    st.write("")

    # Linha 2: plano de hoje (com a semana) + progresso por matéria
    p1, p2 = st.columns([1.15, 1], gap="medium")
    with p1, st.container(border=True, key="card_4"):
        cartao_titulo("🎯 Plano de hoje", f"{MESES[hoje.month - 1]} de {hoje.year}")
        segunda = hoje - dt.timedelta(days=hoje.weekday())
        siglas = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        st.markdown("<div class='cal'>" + "".join(
            f"<div class='{'hoje' if d == hoje else ''}'>{siglas[i]}<b>{d.day:02d}</b></div>"
            for i, d in enumerate(segunda + dt.timedelta(days=n) for n in range(7))) + "</div>",
            unsafe_allow_html=True)
        dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        dia = dias[hoje.weekday()]
        if hoje <= prova and dia in grade:
            linha = grade[dia]
            itens = [(k, str(v)) for k, v in linha.items()
                     if k.startswith("Bloco") and not vazio(v) and str(v).strip() != "-"]
            feitos_plano = sum(plano_feito.get((hoje, f"{k}: {v}"), False) for k, v in itens)
            st.caption(f"{dia} · {linha.get('Tempo Total') or ''} · {feitos_plano} de {len(itens)} feitos")
            for i, (k, v) in enumerate(itens):
                item = f"{k}: {v}"
                chave = f"plano_{hoje}_{i}_v{st.session_state.get('versao', 0)}"
                st.checkbox(f"{v} · _{k}_",
                            value=plano_feito.get((hoje, item), False), key=chave,
                            on_change=lambda it=item, ch=chave: salvar(plano=(hoje, it, st.session_state[ch])))
                aba = materia_do_texto(v)
                prox = proximo_topico(aba) if aba else None
                if prox:
                    st.button(f"📚 Próximo tópico: {topicos.at[prox, 'Cód']} · {topicos.at[prox, 'Tópico'][:55]}",
                              key=f"plano_prox_{i}", on_click=ir, args=("estudar",), kwargs={"estudo_id": prox})
            obs = linha.get("Foco & Orientações")
            if not vazio(obs):
                st.caption(f"💡 {obs}")
            if dia == "Domingo":
                st.button("🧪 Registrar o simulado de hoje", on_click=ir, args=("simulados",), width="stretch",
                          type="primary")
        elif hoje <= fase2:
            st.info("1ª fase concluída. Agora o foco é a peça e as questões discursivas da 2ª fase.")
        else:
            st.info("Exame concluído. Parabéns pelo caminho!")
        if n_rev:
            st.button(f"🔁 Você tem {n_rev} revisão(ões) para hoje", on_click=ir, args=("revisoes",), width="stretch")
    with p2, st.container(border=True, key="card_5"):
        res = resumo_materias(topicos)
        cartao_titulo("Progresso por matéria", "% do edital estudado")
        st.markdown("".join(
            f"<div class='fonte'><span class='nome' title='{r['Matéria']}'>{r['Matéria']}</span>"
            f"<span class='trilho'><div style='width:{r['% Concluído']:.0f}%'></div></span>"
            f"<span class='pct'>{r['% Concluído']:.0f}%</span></div>" for _, r in res.iterrows()),
            unsafe_allow_html=True)
    st.write("")

    # Linha 3: pomodoro + lançar estudo
    c1, c2 = st.columns([1, 1.15], gap="medium")
    with c1, st.container(border=True, key="card_6"):
        cartao_titulo("🍅 Pomodoro")
        pomodoro()
    with c2, st.container(border=True, key="card_7"):
        hoje_reg = registros[registros["Data"] == hoje] if len(registros) else registros
        mins_hoje = hoje_reg["Minutos"].sum() if len(hoje_reg) else 0
        n_pomo = int((hoje_reg["Tipo"] == "Pomodoro").sum()) if len(hoje_reg) else 0
        cartao_titulo("⏱️ Lançar estudo", f"hoje: {fmt_h(mins_hoje / 60)} de {fmt_h(meta / 7)} · {n_pomo} pomodoro(s)")
        registrar_estudo(topicos, "inicio")
    st.write("")
    with st.expander("📊 Ver gráficos de desempenho"):
        res = resumo_materias(topicos)
        mapa = cores(res)
        g1, g2 = st.columns(2)
        with g2:
            com_q = res[res["questoes"] > 0]
            if len(com_q):
                fig = px.bar(com_q, x="Matéria", y="% Acerto", color="Matéria", color_discrete_map=mapa,
                             text="% Acerto", range_y=[0, 105])
                fig.add_hline(y=50, line_dash="dot", line_color=AZUL, annotation_text="meta 50%",
                              annotation_font_color=AZUL)
                fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
                fig.update_xaxes(title=None, tickangle=-25)
                st.plotly_chart(estilo(fig, 420, "Taxa de acertos por matéria"), width="stretch")
            else:
                st.caption("Preencha **Questões** e **Acertos** nas tabelas para ver a taxa de acertos por matéria.")
        with g1:
            if len(registros):
                nome_cor = {v[0]: v[1] for v in MATERIAS.values()}
                hm = registros.groupby("Matéria", as_index=False)["Minutos"].sum()
                hm["Horas"] = (hm["Minutos"] / 60).round(1)
                fig = px.bar(hm.sort_values("Horas"), x="Horas", y="Matéria", orientation="h", color="Matéria",
                             color_discrete_map=nome_cor, text="Horas")
                fig.update_yaxes(title=None)
                st.plotly_chart(estilo(fig, titulo="Horas estudadas por matéria"), width="stretch")
            else:
                st.caption("Registre pomodoros para ver as horas por matéria.")
        peso = res.copy()
        fig = px.scatter(peso, x="Na prova", y="% Concluído", color="Matéria", color_discrete_map=mapa,
                         text="Matéria", size=[max(q, 1) for q in peso["Na prova"]], range_y=[-5, 110])
        fig.update_traces(textposition="top center")
        fig.update_xaxes(title="Questões na prova")
        fig.update_yaxes(title="% do edital estudado")
        st.plotly_chart(estilo(fig, 360, "Peso na prova × quanto você já estudou"), width="stretch")
        st.caption("Matérias à direita e embaixo valem muitas questões e ainda foram pouco estudadas: priorize.")


# ═════════════ Página: grupo (A ou B) ═════════════
def pagina_grupo(chave):
    grp = GRUPOS[chave]
    df = topicos[topicos["Grupo"] == chave]
    mat = st.session_state.get("materia_sel")
    st.markdown(f'<div class="titulo">{grp["icone"]} <span>{grp["nome"]}</span></div>', unsafe_allow_html=True)
    abas = list(dict.fromkeys(df["aba"]))
    if mat:
        abas = list(dict.fromkeys(df.loc[df["Matéria"] == mat, "aba"]))
    q_prova = sum(info_materia(a)[4] for a in abas)
    q_meta = sum(info_materia(a)[5] for a in abas)
    st.markdown(f"<span class='chip'>Banca <b>FGV</b></span>"
                f"<span class='chip'>Prova <b>{prova:%d/%m/%Y}</b> · faltam {(prova - hoje).days} dias</span>"
                f"<span class='chip'><b>{q_prova}</b> questões na prova · meta <b>{q_meta}</b> acertos</span>",
                unsafe_allow_html=True)
    st.write("")

    if mat:
        vis = df[df["Matéria"] == mat]
    else:
        vis = df
    f_ = vis["Status"].isin(FEITO).sum()
    p_ = f_ / len(vis) * 100 if len(vis) else 0
    a1, a2, a3 = st.columns(3)
    with a1:
        kpi("Edital estudado", fmt_p(p_), f"{f_} de {len(vis)} tópicos", p_, "📚", destaque=True)
    with a2:
        kpi("Taxa de acertos", fmt_p(taxa_acerto(vis)), f"{int(vis['Nº Questões'].sum())} questões", taxa_acerto(vis), "🎯")
    with a3:
        kpi("Revisões para hoje", f"{len(revisoes_pendentes(vis, hoje))}", "deste grupo" if not mat else "desta matéria", None, "🔁")
    st.write("")

    if mat:
        st.markdown(f"### {mat}")
    else:
        res_c = resumo_materias(df)
        fig = px.bar(res_c, x="Matéria", y="% Concluído", color="Matéria", color_discrete_map=cores(res_c),
                     text="% Concluído", range_y=[0, 110])
        fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
        fig.update_xaxes(title=None, tickangle=-20)
        st.plotly_chart(estilo(fig, 260, "Progresso por matéria"), width="stretch", key=f"graf_{chave}")

    filtro = st.pills("Status", STATUS, selection_mode="multi", default=STATUS, key=f"st_{chave}_{mat}")
    vis = vis[vis["Status"].isin(filtro or STATUS)]
    st.caption("✏️ Clique numa célula para editar. Cada alteração é salva sozinha na planilha original. "
               "O % de acerto é calculado sozinho.")
    if len(vis):
        tabela_editavel(vis, f"tab_{chave}_{mat}")
        c1, c2 = st.columns([3, 1])
        abrir = c1.selectbox("Estudar um tópico desta lista", list(vis.index),
                             format_func=lambda i: f"{vis.at[i, 'Cód']} · {vis.at[i, 'Tópico']}",
                             key=f"abrir_{chave}_{mat}", label_visibility="collapsed")
        c2.button("📚 Estudar este tópico", width="stretch", on_click=ir, args=("estudar",),
                  kwargs={"estudo_id": abrir}, key=f"btn_abrir_{chave}_{mat}")
    else:
        st.caption("Nenhum tópico com esses filtros.")


# ═════════════ Materiais do curso (videoaulas e PDFs) ═════════════
def materiais(cod):
    nota = ler_anotacoes().get(cod, {})
    links = nota.get("links", [])
    st.markdown("#### 🎬 Videoaulas e links")
    if links:
        for n, link in enumerate(links, 1):
            st.link_button(f"▶ Abrir aula {n} · {link[:60]}", link, width="stretch")
    else:
        st.caption("Nenhum link ainda. Copie o endereço da aula no site do seu curso e cole abaixo.")
    with st.form(f"link_{cod}", clear_on_submit=True):
        novo = st.text_input("Colar link da videoaula", placeholder="https://...")
        if st.form_submit_button("➕ Adicionar link") and novo.strip():
            salvar_anotacao(cod, links=links + [novo.strip()])
            st.rerun()

    st.markdown("#### 📄 PDFs")
    PASTA_MATERIAIS.mkdir(exist_ok=True)
    todos_pdfs = sorted(p.relative_to(PASTA_MATERIAIS).as_posix() for p in PASTA_MATERIAIS.rglob("*.pdf"))
    # Entram sozinhos os PDFs com o código do tópico no nome (ex.: "ETI.04 Honorários.pdf").
    marcador = cod.lower()
    vinculados = [p for p in todos_pdfs if marcador in p.lower()] + \
        [p for p in nota.get("pdfs", []) if p in todos_pdfs and marcador not in p.lower()]
    if not todos_pdfs:
        st.caption(f"Coloque os PDFs baixados do curso na pasta **materiais**, dentro de {BASE.name}. "
                   f"Se o nome do arquivo tiver o código {cod}, ele aparece aqui sozinho.")
    if vinculados:
        escolhido = st.selectbox("PDF", vinculados, key=f"pdf_sel_{cod}") if len(vinculados) > 1 else vinculados[0]
        caminho = PASTA_MATERIAIS / escolhido
        dados = caminho.read_bytes()
        try:
            st.pdf(dados, height=700)
        except Exception:
            st.caption("Para ver o PDF aqui dentro, rode uma vez: pip install streamlit-pdf")
        st.download_button(f"⬇️ Abrir {caminho.name}", dados, file_name=caminho.name, mime="application/pdf",
                           key=f"pdf_dl_{cod}")
    outros = [p for p in todos_pdfs if p not in vinculados]
    if outros:
        with st.expander("Vincular outro PDF da pasta materiais a este tópico"):
            extra = st.selectbox("Arquivo", outros, key=f"pdf_add_{cod}")
            if st.button("🔗 Vincular", key=f"pdf_btn_{cod}"):
                salvar_anotacao(cod, pdfs=nota.get("pdfs", []) + [extra])
                st.rerun()


# ═════════════ Página: estudar ═════════════
def pagina_estudar():
    st.markdown('<div class="titulo">📚 <span>Estudar</span></div>', unsafe_allow_html=True)
    ids = list(topicos.index)
    atual = st.session_state.get("estudo_id")
    if atual not in ids:
        atual = ids[0]
    c1, c2 = st.columns([1, 2])
    mats = list(dict.fromkeys(topicos["Matéria"]))
    mat = c1.selectbox("Matéria", mats, index=mats.index(topicos.at[atual, "Matéria"]), key=f"est_mat_{atual}")
    sub = topicos[topicos["Matéria"] == mat]
    if atual not in sub.index:
        atual = sub.index[0]
    escolhido = c2.selectbox("Tópico", list(sub.index), index=list(sub.index).index(atual),
                             format_func=lambda i: f"{sub.at[i, 'Cód']} · {sub.at[i, 'Tópico']}", key=f"est_top_{mat}_{atual}")
    if escolhido != st.session_state.get("estudo_id"):
        st.session_state.estudo_id = escolhido
        st.rerun()
    t = topicos.loc[escolhido]
    cod = t["Cód"]
    _, _, _, grupo, q_prova, _ = info_materia(t["aba"])
    st.markdown(f"<span class='chip' style='border-color:{t['Cor']}'>{t['Matéria']}</span>"
                f"<span class='chip'>Cód <b>{cod}</b></span><span class='chip'>Grupo <b>{grupo}</b> · "
                f"{q_prova} questões na prova</span>"
                f"<span class='chip'>Status <b>{t['Status']}</b></span>", unsafe_allow_html=True)
    st.markdown(f"## {t['Tópico']}")

    conteudo = base_estudos.get(cod, {"resumo": "", "flashcards": []})
    analise = banca.get(cod, {"palavras": [], "FGV": ""})
    aba_res, aba_pts, aba_banca, aba_mat, aba_fc, aba_nota, aba_prog = st.tabs(
        ["📖 Resumo", "📌 Pontos para anotar", "🎯 Como a FGV cobra", "🎬 Materiais", "🃏 Flashcards",
         "✍️ Minhas anotações", "✅ Progresso"])
    with aba_mat:
        materiais(cod)
    with aba_res:
        if analise["palavras"]:
            st.markdown("🔑 " + "".join(f"<span class='chip'>{p}</span>" for p in analise["palavras"]),
                        unsafe_allow_html=True)
            st.write("")
        if conteudo["resumo"]:
            st.markdown(conteudo["resumo"])
            st.caption("Resumo de apoio. Confira sempre na lei seca, nas súmulas e no edital.")
        else:
            st.info(f"Ainda não há resumo para {cod}. Escreva o seu em **Minhas anotações** ou acrescente "
                    f"na pasta base_estudos.")
    with aba_pts:
        pontos = pontos_do_resumo(conteudo["resumo"])
        if pontos:
            st.caption("Os pontos que mais caem neste tópico. Copie para as suas anotações e complete com as suas palavras.")
            for n, ponto in enumerate(pontos, 1):
                st.markdown(f"**{n}.** {ponto}")
            if st.button("➕ Copiar pontos para Minhas anotações", key=f"copiar_{cod}"):
                nota_atual = ler_anotacoes().get(cod, {})
                texto_novo = (nota_atual.get("texto", "").rstrip() + "\n\n" if nota_atual.get("texto") else "") + \
                    "\n".join(f"- {p}" for p in pontos)
                salvar_anotacao(cod, texto=texto_novo)
                st.toast("Pontos copiados para Minhas anotações ✓", icon="📌")
        else:
            st.info("Ainda não há pontos para este tópico.")
    with aba_banca:
        st.markdown("#### ⚖️ FGV · Exame de Ordem")
        st.markdown(f"<div class='resumo'><b>Neste assunto:</b> {analise['FGV'] or 'sem análise cadastrada.'}"
                    f"<br><br><small style='color:{APAGADO}'>Estilo da banca: {PERFIL_FGV}</small></div>",
                    unsafe_allow_html=True)
        st.write("")
        st.caption("Tendências observadas em exames anteriores, e não garantia de cobrança. Resolva provas recentes da FGV.")
    with aba_fc:
        cartas = conteudo["flashcards"]
        if not cartas:
            st.info("Ainda não há flashcards para este tópico.")
        else:
            k = f"fc_{cod}"
            st.session_state.setdefault(k, 0)
            i = st.session_state[k] % len(cartas)
            mostrar = st.session_state.get(f"{k}_ver", False)
            pergunta, resposta = cartas[i]
            st.markdown(f"<div class='flash'><small>Cartão {i + 1} de {len(cartas)}</small>{pergunta}</div>",
                        unsafe_allow_html=True)
            if mostrar:
                st.markdown(f"<div class='flash' style='margin-top:10px;border-color:{AZUL_CLARO}'>"
                            f"<small>Resposta</small>{resposta}</div>", unsafe_allow_html=True)
            st.write("")
            b1, b2, b3 = st.columns(3)
            b1.button("👁️ Mostrar resposta", width="stretch", key=f"{k}_b1",
                      on_click=lambda: st.session_state.update({f"{k}_ver": True}))
            b2.button("◀ Anterior", width="stretch", key=f"{k}_b2",
                      on_click=lambda: st.session_state.update({k: i - 1, f"{k}_ver": False}))
            b3.button("Próximo ▶", width="stretch", key=f"{k}_b3",
                      on_click=lambda: st.session_state.update({k: i + 1, f"{k}_ver": False}))
    with aba_nota:
        nota = ler_anotacoes().get(cod, {})
        with st.form(f"nota_{cod}"):
            texto = st.text_area("Suas anotações (aceita **negrito**, listas com - etc.)", nota.get("texto", ""),
                                 height=260)
            links = st.text_area("Links de aulas, PDFs e leis (um por linha)", "\n".join(nota.get("links", [])), height=90)
            if st.form_submit_button("💾 Salvar anotações"):
                salvar_anotacao(cod, texto=texto, links=[l.strip() for l in links.splitlines() if l.strip()])
                st.toast("Anotações salvas ✓", icon="✍️")
        if nota.get("links"):
            st.markdown("**Links salvos:**  \n" + "  \n".join(f"- {l}" for l in nota["links"]))
    with aba_prog:
        n1, n2 = st.columns(2)
        novo_status = n1.selectbox("Status do tópico", STATUS, index=STATUS.index(t["Status"]), key=f"status_{cod}")
        if novo_status != t["Status"]:
            alt = [(escolhido, "Status", novo_status)]
            if novo_status in FEITO and not t["Data Estudada"]:
                alt.append((escolhido, "Data Estudada", hoje))
            if salvar(alt):
                avisar(f"{cod} marcado como {novo_status} ✓", "✅")
                st.rerun()
        n2.metric("Questões · acertos", f"{t['Nº Questões']} · {t['Acertos']} ({t['% Acerto']:.0f}%)")
        with st.form(f"questoes_{cod}", clear_on_submit=True):
            st.caption("Fez questões deste tópico? Some aqui.")
            q1, q2 = st.columns(2)
            mais_q = q1.number_input("Questões feitas agora", 0, 500, 0, 1)
            mais_a = q2.number_input("Acertos", 0, 500, 0, 1)
            if st.form_submit_button("➕ Somar questões") and mais_q:
                tot_q = t["Nº Questões"] + mais_q
                tot_a = min(t["Acertos"] + min(mais_a, mais_q), tot_q)
                if salvar([(escolhido, "Nº Questões", tot_q), (escolhido, "Acertos", tot_a)]):
                    avisar(f"{mais_q} questões somadas em {cod} ✓", "📝")
                    st.rerun()
        registrar_estudo(topicos, f"est_{cod}", cod_fixo=cod)

    pos = ids.index(escolhido)
    st.write("")
    p1, _, p2 = st.columns([1, 2, 1])
    if pos > 0:
        p1.button("◀ Tópico anterior", width="stretch", on_click=ir, args=("estudar",), kwargs={"estudo_id": ids[pos - 1]})
    if pos < len(ids) - 1:
        p2.button("Próximo tópico ▶", width="stretch", on_click=ir, args=("estudar",), kwargs={"estudo_id": ids[pos + 1]})


# ═════════════ Página: revisões ═════════════
def pagina_revisoes():
    st.markdown('<div class="titulo">🔁 <span>Revisões</span></div>', unsafe_allow_html=True)
    st.caption("O plano usa revisão de 7 dias, contada a partir de **Estudado em** (aos sábados, 1h de revisão ativa). "
               "Marque ✔ quando fizer: fica gravado como 'Feito' e o tópico passa para 'Revisado (7d)'.")
    pend = revisoes_pendentes(topicos, hoje)
    if pend.empty:
        st.success("Nenhuma revisão vencida. 👏")
    else:
        pend = pend.sort_values("Vence em").reset_index(drop=True)
        pend.insert(0, "Feito", False)
        ed = st.data_editor(
            pend, hide_index=True, width="stretch", key=f"rev_v{st.session_state.get('versao', 0)}",
            column_order=["Feito", "Matéria", "Cód", "Tópico", "Revisão", "Vence em", "Atraso (dias)"],
            disabled=["Matéria", "Cód", "Tópico", "Revisão", "Vence em", "Atraso (dias)"],
            column_config={"Feito": st.column_config.CheckboxColumn("✔", width="small"),
                           "Vence em": st.column_config.DateColumn("Vence em", format="DD/MM/YYYY"),
                           "Tópico": st.column_config.TextColumn(width="large")})
        marcadas = ed[ed["Feito"]]
        if len(marcadas):
            alt = [(r["id"], r["Coluna"], "Feito") for _, r in marcadas.iterrows()]
            for ident in marcadas["id"].unique():
                if topicos.at[ident, "Status"] in ("Em Teoria", "Estudado"):
                    alt.append((ident, "Status", "Revisado (7d)"))
            if salvar(alt):
                avisar("Revisão registrada ✓", "🔁")
                st.rerun()
    prox = revisoes_pendentes(topicos, hoje + dt.timedelta(days=7))
    prox = prox[prox["Vence em"] > hoje] if not prox.empty else prox
    if not prox.empty:
        with st.expander(f"Próximos 7 dias · {len(prox)} revisões"):
            st.dataframe(prox.sort_values("Vence em")[["Vence em", "Matéria", "Cód", "Tópico", "Revisão"]],
                         hide_index=True, width="stretch",
                         column_config={"Vence em": st.column_config.DateColumn(format="DD/MM/YYYY")})


# ═════════════ Página: simulados ═════════════
def pagina_simulados():
    st.markdown('<div class="titulo">🧪 <span>Simulados</span></div>', unsafe_allow_html=True)
    st.caption(f"Todo domingo: {TOTAL_QUESTOES} questões no tempo de prova (5h), depois revise o gabarito e "
               f"anote os erros no tópico. A aprovação na 1ª fase pede {META_APROVACAO} acertos.")
    with st.form("novo_simulado", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 2])
        data = c1.date_input("Data", hoje, format="DD/MM/YYYY")
        acertos = c2.number_input(f"Acertos (de {TOTAL_QUESTOES})", 0, TOTAL_QUESTOES, 40, 1)
        obs = c3.text_input("Observações", placeholder="Ex.: errei muito Processo Civil (recursos)")
        if st.form_submit_button("💾 Registrar simulado"):
            if salvar(simulado=(data, int(acertos), obs.strip())):
                avisar("Simulado registrado ✓", "🧪")
                st.rerun()
    if not len(simulados):
        st.info("Nenhum simulado registrado ainda. O primeiro é no próximo domingo.")
        return
    ult, melhor = simulados.iloc[-1], simulados["Acertos"].max()
    m1, m2, m3 = st.columns(3)
    with m1:
        kpi("Último simulado", f"{ult['Acertos']}/{TOTAL_QUESTOES}", f"{ult['Data']:%d/%m/%Y}",
            ult["Acertos"] / TOTAL_QUESTOES * 100, "🧪", destaque=True)
    with m2:
        kpi("Melhor resultado", f"{melhor}/{TOTAL_QUESTOES}", "", melhor / TOTAL_QUESTOES * 100, "🏆")
    with m3:
        acima = int((simulados["Acertos"] >= META_APROVACAO).sum())
        kpi("Simulados aprovados", f"{acima} de {len(simulados)}", f"com {META_APROVACAO}+ acertos",
            acima / len(simulados) * 100, "✅")
    st.write("")
    fig = go.Figure(go.Scatter(x=simulados["Data"], y=simulados["Acertos"], mode="lines+markers+text",
                               text=simulados["Acertos"], textposition="top center",
                               line=dict(color=AZUL, width=3), marker=dict(size=9, color=AZUL)))
    fig.add_hline(y=META_APROVACAO, line_dash="dot", line_color=APAGADO,
                  annotation_text=f"aprovação: {META_APROVACAO}", annotation_font_color=APAGADO)
    fig.update_yaxes(range=[0, TOTAL_QUESTOES])
    fig.update_xaxes(tickformat="%d/%m")
    st.plotly_chart(estilo(fig, 340, "Evolução nos simulados"), width="stretch")
    tab = simulados.sort_values("Data", ascending=False).copy()
    tab["% Acerto"] = (tab["Acertos"] / TOTAL_QUESTOES * 100).round(1)
    st.dataframe(tab, hide_index=True, width="stretch",
                 column_config={"Data": st.column_config.DateColumn(format="DD/MM/YYYY"),
                                "% Acerto": st.column_config.NumberColumn(format="%.0f%%")})


# ═════════════ Página: resumo do dia ═════════════
def topicos_do_dia():
    """Tópicos estudados hoje, com estudo registrado hoje ou que são os próximos das matérias do dia."""
    ids = set(topicos.index[topicos["Data Estudada"] == hoje])
    if len(registros):
        cods = set(registros.loc[registros["Data"] == hoje, "Cód"].dropna().astype(str))
        ids |= set(topicos.index[topicos["Cód"].isin(cods)])
    dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    for k, v in grade.get(dias[hoje.weekday()], {}).items():
        aba = materia_do_texto(v) if k.startswith("Bloco") else None
        prox = proximo_topico(aba) if aba else None
        if prox:
            ids.add(prox)
    return [i for i in topicos.index if i in ids]


def pagina_resumo_dia():
    st.markdown('<div class="titulo">📝 Resumo <span>do dia</span></div>', unsafe_allow_html=True)
    st.caption(f"{hoje:%d/%m/%Y} · Junta resumo, pontos para anotar, palavras-chave e como a FGV cobra, separados por matéria.")
    sugeridos = topicos_do_dia()
    escolha = st.multiselect(
        "Assuntos de hoje", list(topicos.index), default=sugeridos, key=f"resumo_dia_{hoje}",
        format_func=lambda i: f"{topicos.at[i, 'Matéria'].split(' ', 1)[0]} {topicos.at[i, 'Cód']} · {topicos.at[i, 'Tópico'][:60]}",
        placeholder="Escolha os assuntos que você estudou ou vai estudar hoje")
    if not sugeridos:
        st.caption("Dica: os assuntos entram aqui sozinhos quando são das matérias do dia no cronograma, "
                   "quando têm data de estudo hoje ou quando você registra um pomodoro neles.")
    if not escolha:
        return
    texto_md = [f"# Resumo do dia · {hoje:%d/%m/%Y}\n"]
    sel = topicos.loc[escolha]
    for mat, grupo in sel.groupby("Matéria", sort=False):
        st.markdown(f"## {mat}")
        texto_md.append(f"\n## {mat}\n")
        for ident, t in grupo.iterrows():
            cod = t["Cód"]
            conteudo = base_estudos.get(cod, {"resumo": ""})
            analise = banca.get(cod, {"palavras": [], "FGV": ""})
            pontos = pontos_do_resumo(conteudo["resumo"])
            with st.expander(f"{cod} · {t['Tópico']}", expanded=True):
                if analise["palavras"]:
                    st.markdown("🔑 " + "".join(f"<span class='chip'>{p}</span>" for p in analise["palavras"]),
                                unsafe_allow_html=True)
                if pontos:
                    st.markdown("**📌 Pontos para anotar**\n" + "\n".join(f"- {p}" for p in pontos))
                if analise["FGV"]:
                    st.markdown(f"**🎯 FGV:** {analise['FGV']}")
                st.button("📚 Abrir para estudar", key=f"rd_abrir_{ident}", on_click=ir, args=("estudar",),
                          kwargs={"estudo_id": ident})
            texto_md.append(f"\n### {cod} · {t['Tópico']}\n")
            if analise["palavras"]:
                texto_md.append("Palavras-chave: " + "; ".join(analise["palavras"]) + "\n")
            texto_md += [f"- {p}" for p in pontos]
            if analise["FGV"]:
                texto_md.append(f"\nComo a FGV cobra: {analise['FGV']}")
    st.download_button("⬇️ Baixar resumo do dia", "\n".join(texto_md), file_name=f"resumo_{hoje:%Y-%m-%d}.md",
                       mime="text/markdown")


barra_topo()
if pagina.startswith("grupo:"):
    pagina_grupo(pagina.split(":", 1)[1])
elif pagina == "estudar":
    pagina_estudar()
elif pagina == "resumo_dia":
    pagina_resumo_dia()
elif pagina == "revisoes":
    pagina_revisoes()
elif pagina == "simulados":
    pagina_simulados()
else:
    pagina_inicio()
