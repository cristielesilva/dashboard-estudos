"""
Núcleo da dashboard CSA Advocacia: dados, captura de intimações no DJEN (CNJ), cálculo de prazos e petições.
Usado pelo app (app.py) e pela captura diária automática (capturar.py).
"""
import datetime as dt
import json
import os
import re
import shutil
import unicodedata
import uuid
from pathlib import Path

import requests

BASE = Path(__file__).parent
PASTA_DADOS = Path(os.environ.get("CSA_DADOS", BASE / "dados"))
ARQ_DADOS = PASTA_DADOS / "escritorio.json"
PASTA_BACKUP = PASTA_DADOS / "backup"
PASTA_MODELOS = BASE / "modelos"

# API pública do Diário de Justiça Eletrônico Nacional (Comunica PJe / CNJ). Não precisa de login.
DJEN_URL = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
DJEN_SITE = "https://comunica.pje.jus.br/consulta"

CONFIG_PADRAO = {
    "escritorio": "CSA ADVOCACIA",
    "advogada": "Cristiele Silva",
    "cidade": "Recife",
    "uf_padrao": "PE",
    "oabs": [],          # [{"numero": "12345", "uf": "PE"}]  -> processos em que você é patrona
    "parceiros": [],     # [{"nome": "Dr. Fulano", "numero": "54321", "uf": "PE"}] -> processos de parceria
    "dias_busca": 7,     # quantos dias para trás buscar a cada captura
    "feriados_extras": [],  # ["2026-06-24", ...] feriados locais (estado, município, tribunal)
    "feriados_moveis": False,  # contar Carnaval, Quarta/Quinta Santas e Corpus Christi como dias sem prazo
}


def novo_banco():
    return {"config": dict(CONFIG_PADRAO), "intimacoes": {}, "processos": {}, "prazos": [], "tarefas": [],
            "rascunhos": [], "modelos_custom": {}, "ultima_busca": None, "log_buscas": []}


def ler_dados():
    if ARQ_DADOS.exists():
        try:
            banco = json.loads(ARQ_DADOS.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            banco = novo_banco()
    else:
        banco = novo_banco()
    padrao = novo_banco()
    for k, v in padrao.items():
        banco.setdefault(k, v)
    for k, v in CONFIG_PADRAO.items():
        banco["config"].setdefault(k, v)
    return banco


def gravar_dados(banco):
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    if ARQ_DADOS.exists():
        PASTA_BACKUP.mkdir(exist_ok=True)
        hoje = dt.date.today().isoformat()
        destino = PASTA_BACKUP / f"escritorio_{hoje}.json"
        if not destino.exists():  # uma cópia por dia, guarda as 15 últimas
            shutil.copy2(ARQ_DADOS, destino)
            for velho in sorted(PASTA_BACKUP.glob("escritorio_*.json"))[:-15]:
                velho.unlink(missing_ok=True)
    tmp = ARQ_DADOS.with_suffix(".tmp")
    tmp.write_text(json.dumps(banco, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(ARQ_DADOS)


def novo_id():
    return uuid.uuid4().hex[:10]


def sem_acento(txt):
    return "".join(c for c in unicodedata.normalize("NFD", str(txt or "")) if unicodedata.category(c) != "Mn").lower()


def so_digitos(txt):
    return re.sub(r"\D", "", str(txt or ""))


def mascara_cnj(num):
    d = so_digitos(num)
    if len(d) != 20:
        return str(num or "")
    return f"{d[:7]}-{d[7:9]}.{d[9:13]}.{d[13]}.{d[14:16]}.{d[16:]}"


def para_data(v):
    if not v:
        return None
    if isinstance(v, dt.date):
        return v
    try:
        return dt.date.fromisoformat(str(v)[:10])
    except ValueError:
        try:
            return dt.datetime.strptime(str(v)[:10], "%d/%m/%Y").date()
        except ValueError:
            return None


def br(d):
    d = para_data(d)
    return d.strftime("%d/%m/%Y") if d else ""


# ───────────────────────── Feriados e dias úteis ─────────────────────────
def pascoa(ano):
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    mes = (h + l_ - 7 * m + 114) // 31
    dia = ((h + l_ - 7 * m + 114) % 31) + 1
    return dt.date(ano, mes, dia)


def feriados_do_ano(ano, moveis=False):
    """Feriados nacionais (Lei 662/1949, Lei 6.802/1980, Lei 14.759/2023) e a Sexta-feira Santa.
    Carnaval, Quarta e Quinta Santas e Corpus Christi só entram se você ligar a opção (variam por tribunal).
    Na dúvida o app conta MENOS feriados: o vencimento calculado nunca fica depois do real."""
    p = pascoa(ano)
    fixos = [(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20), (12, 25)]
    dias = {dt.date(ano, m, d) for m, d in fixos}
    dias.add(p - dt.timedelta(days=2))  # Sexta-feira Santa
    if moveis:
        dias.update(p + dt.timedelta(days=x) for x in (-48, -47, -4, -3, 60))
    return dias


def suspenso(d, extras=(), moveis=False):
    """Dia em que o prazo não corre: fim de semana, feriado ou recesso (20/12 a 20/01, art. 220 do CPC)."""
    if d.weekday() >= 5:
        return True
    if (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 20):
        return True
    return d in feriados_do_ano(d.year, moveis) or d.isoformat() in set(extras)


def proximo_util(d, extras=(), moveis=False):
    d += dt.timedelta(days=1)
    while suspenso(d, extras, moveis):
        d += dt.timedelta(days=1)
    return d


def somar_uteis(d, n, extras=(), moveis=False):
    for _ in range(n):
        d = proximo_util(d, extras, moveis)
    return d


def calcular_prazo(disponibilizacao, dias, uteis=True, extras=(), moveis=False):
    """DJEN: publicação = 1º dia útil depois da disponibilização; o prazo começa no 1º dia útil seguinte
    (Lei 11.419/2006, art. 4º, §§ 3º e 4º; CPC, arts. 219 e 224). Devolve (publicação, início, vencimento)."""
    disp = para_data(disponibilizacao)
    publicacao = proximo_util(disp, extras, moveis)
    inicio = proximo_util(publicacao, extras, moveis)
    if uteis:
        venc = somar_uteis(publicacao, dias, extras, moveis)
    else:
        venc = publicacao + dt.timedelta(days=dias)
        while suspenso(venc, extras, moveis):  # se cair em dia sem expediente, vai para o próximo dia útil
            venc += dt.timedelta(days=1)
    return publicacao, inicio, venc


# ───────────────────────── DJEN: captura de intimações ─────────────────────────
class ErroDJEN(Exception):
    pass


def buscar_djen(numero_oab, uf, inicio, fim, max_paginas=20):
    """Busca as comunicações publicadas no DJEN para uma OAB entre duas datas."""
    itens, pagina = [], 1
    while pagina <= max_paginas:
        params = {"numeroOab": so_digitos(numero_oab), "ufOab": uf.upper(),
                  "dataDisponibilizacaoInicio": inicio.isoformat(), "dataDisponibilizacaoFim": fim.isoformat(),
                  "pagina": pagina, "itensPorPagina": 100}
        try:
            r = requests.get(DJEN_URL, params=params, timeout=40,
                             headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0 (painel-escritorio)"})
        except requests.RequestException as erro:
            raise ErroDJEN(f"Sem conexão com o DJEN ({erro.__class__.__name__}). Verifique a internet.") from erro
        if r.status_code == 429:
            raise ErroDJEN("O DJEN pediu para esperar (muitas consultas seguidas). Tente de novo em alguns minutos.")
        if r.status_code in (401, 403):
            raise ErroDJEN(f"O DJEN recusou a consulta (código {r.status_code}). Isso costuma acontecer quando o app "
                           "roda fora do Brasil (versão online). Rode a captura no seu computador.")
        if r.status_code != 200:
            raise ErroDJEN(f"O DJEN respondeu com erro {r.status_code}. Tente mais tarde.")
        try:
            corpo = r.json()
        except ValueError as erro:
            raise ErroDJEN("O DJEN devolveu uma resposta que não consegui ler.") from erro
        lote = corpo.get("items") or corpo.get("itens") or []
        itens.extend(lote)
        total = corpo.get("count") or 0
        if not lote or len(itens) >= total or len(lote) < 100:
            break
        pagina += 1
    return itens


def limpar_html(txt):
    txt = re.sub(r"<br\s*/?>|</p>", "\n", str(txt or ""), flags=re.I)
    txt = re.sub(r"<[^>]+>", "", txt)
    txt = (txt.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
           .replace("&lt;", "<").replace("&gt;", ">"))
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def normalizar_item(item, origem):
    """Converte um item do DJEN no formato usado pela dashboard."""
    numero = so_digitos(item.get("numero_processo") or item.get("numeroProcesso") or "")
    partes = []
    for d in item.get("destinatarios") or []:
        nome = (d.get("nome") or "").strip()
        if nome:
            partes.append({"nome": nome, "polo": d.get("polo") or ""})
    advogados = []
    for a in item.get("destinatarioadvogados") or []:
        adv = a.get("advogado") or a
        advogados.append({"nome": adv.get("nome", ""), "oab": f"{adv.get('numero_oab', '')}/{adv.get('uf_oab', '')}"})
    ident = str(item.get("id") or item.get("hash") or novo_id())
    return {
        "id": ident,
        "data": str(item.get("data_disponibilizacao") or item.get("datadisponibilizacao") or "")[:10],
        "tribunal": item.get("siglaTribunal") or "",
        "orgao": item.get("nomeOrgao") or "",
        "tipo": item.get("tipoComunicacao") or "",
        "documento": item.get("tipoDocumento") or "",
        "classe": item.get("nomeClasse") or "",
        "processo": numero,
        "processo_fmt": item.get("numeroprocessocommascara") or mascara_cnj(numero),
        "texto": limpar_html(item.get("texto")),
        "link": item.get("link") or "",
        "partes": partes,
        "advogados": advogados,
        "origem": origem,  # "patrona" ou nome do parceiro
        "lida": False,
        "capturada_em": dt.datetime.now().isoformat(timespec="minutes"),
    }


def capturar(banco, dias=None, hoje=None):
    """Busca as intimações de todas as OABs cadastradas e junta no banco. Devolve (novas, erros)."""
    cfg = banco["config"]
    hoje = hoje or dt.date.today()
    dias = dias or int(cfg.get("dias_busca") or 7)
    inicio = hoje - dt.timedelta(days=dias)
    alvos = [(o, "patrona") for o in cfg.get("oabs", [])] + [(p, p.get("nome") or "Parceria") for p in cfg.get("parceiros", [])]
    novas, erros = 0, []
    for oab, origem in alvos:
        if not oab.get("numero"):
            continue
        try:
            itens = buscar_djen(oab["numero"], oab.get("uf") or cfg.get("uf_padrao", "PE"), inicio, hoje)
        except ErroDJEN as erro:
            erros.append(f"OAB {oab['numero']}/{oab.get('uf', '')}: {erro}")
            continue
        for item in itens:
            nova = normalizar_item(item, origem)
            atual = banco["intimacoes"].get(nova["id"])
            if atual:
                if atual.get("origem") != "patrona" and origem == "patrona":
                    atual["origem"] = "patrona"
                continue
            banco["intimacoes"][nova["id"]] = nova
            vincular_processo(banco, nova)
            novas += 1
    banco["ultima_busca"] = dt.datetime.now().isoformat(timespec="minutes")
    banco["log_buscas"] = (banco.get("log_buscas") or [])[-29:] + [
        {"quando": banco["ultima_busca"], "novas": novas, "erros": erros}]
    return novas, erros


def vincular_processo(banco, intim):
    """Cria (ou atualiza) o processo da intimação. Intimação pela OAB de parceiro = processo de parceria."""
    num = intim["processo"]
    if not num:
        return
    proc = banco["processos"].get(num)
    if not proc:
        proc = {"numero": num, "numero_fmt": intim["processo_fmt"], "cliente": "", "parte_contraria": "",
                "tribunal": intim["tribunal"], "orgao": intim["orgao"], "classe": intim["classe"],
                "tipo": "Patrona" if intim["origem"] == "patrona" else "Parceria",
                "parceiro": "" if intim["origem"] == "patrona" else intim["origem"],
                "honorarios": "", "status": "Ativo", "observacoes": "",
                "partes": intim["partes"], "criado": dt.date.today().isoformat()}
        banco["processos"][num] = proc
    if intim["origem"] == "patrona" and proc.get("tipo") == "Parceria" and not proc.get("parceiro"):
        proc["tipo"] = "Patrona"
    nomes = {p["nome"] for p in proc.get("partes", [])}
    proc.setdefault("partes", []).extend(p for p in intim["partes"] if p["nome"] not in nomes)
    if intim["data"] >= (proc.get("ultima_mov") or ""):
        proc["ultima_mov"] = intim["data"]
        proc["ultima_mov_resumo"] = resumo(intim["texto"], 160)
    if not proc.get("orgao"):
        proc["orgao"] = intim["orgao"]


def resumo(txt, n=220):
    t = " ".join(str(txt or "").split())
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


# ───────────────────────── Leitura da intimação: qual peça e qual prazo ─────────────────────────
# (palavras-chave, peça sugerida, prazo cível em dias úteis, prazo trabalhista)
REGRAS = [
    (["audiencia"], "Audiência designada", None, None),
    (["contrarrazo", "contrarrazoar", "apresentar resposta ao recurso"], "Contrarrazões", 15, 8),
    (["embargos de declaracao"], "Manifestação sobre embargos de declaração", 5, 5),
    (["sentenca", "julgo procedente", "julgo improcedente", "julgo parcialmente", "julgo extinto"], "Apelação", 15, 8),
    (["replica", "sobre a contestacao", "impugnacao a contestacao", "impugnar a contestacao"], "Réplica", 15, 15),
    (["emend", "emenda a inicial"], "Emenda à inicial", 15, 15),
    (["especificar", "especifiquem", "provas que pretendem"], "Especificação de provas", 15, 5),
    (["laudo", "pericia", "perito"], "Manifestação sobre laudo pericial", 15, 5),
    (["custas", "preparo", "recolh"], "Comprovação de custas", 5, 5),
    (["alvara", "levantamento"], "Pedido de expedição de alvará", 5, 5),
    (["calculos", "cumprimento de sentenca", "impugnacao ao cumprimento"], "Manifestação sobre cálculos", 15, 8),
    (["tutela", "liminar", "defiro", "indefiro"], "Agravo de instrumento", 15, None),
]
MODELO_DA_PECA = {
    "Contrarrazões": "Contrarrazões de recurso", "Manifestação sobre embargos de declaração": "Manifestação simples",
    "Apelação": "Apelação", "Réplica": "Réplica à contestação", "Emenda à inicial": "Emenda à inicial",
    "Especificação de provas": "Especificação de provas", "Manifestação sobre laudo pericial": "Manifestação simples",
    "Comprovação de custas": "Juntada de documentos", "Pedido de expedição de alvará": "Pedido de alvará",
    "Manifestação sobre cálculos": "Manifestação simples", "Agravo de instrumento": "Agravo de instrumento",
    "Embargos de declaração": "Embargos de declaração", "Manifestação": "Manifestação simples",
    "Recurso ordinário": "Apelação", "Recurso inominado": "Apelação",
}
NUMEROS = {"um": 1, "dois": 2, "tres": 3, "cinco": 5, "dez": 10, "quinze": 15, "trinta": 30, "oito": 8, "quarenta e oito": 2}


def prazo_no_texto(t):
    """Procura "prazo de 05 (cinco) dias" no texto. Devolve o número de dias ou None."""
    m = re.search(r"prazo (?:comum |legal |sucessivo )?de (\d{1,2})\s*(?:\([a-z ]+\))?\s*(?:dias|horas)", t)
    if m:
        n = int(m.group(1))
        return 2 if "horas" in t[m.start():m.end()] and n == 48 else n
    m = re.search(r"prazo (?:comum |legal )?de ([a-z ]+?) dias", t)
    if m and m.group(1).strip() in NUMEROS:
        return NUMEROS[m.group(1).strip()]
    return None


def analisar(intim):
    """Sugere a peça, o prazo (dias úteis) e eventual data de audiência a partir do texto da intimação."""
    t = sem_acento(f"{intim.get('documento', '')} {intim.get('texto', '')}")
    trabalhista = str(intim.get("tribunal", "")).upper().startswith("TRT")
    juizado = "juizado" in sem_acento(intim.get("orgao", "") + intim.get("classe", ""))
    peca, dias = "Manifestação", 5  # CPC, art. 218, § 3º: sem prazo fixado, 5 dias
    for chaves, nome, civel, trab in REGRAS:
        if any(c in t for c in chaves):
            if trabalhista and trab is None and civel is not None:
                continue
            peca, dias = nome, (trab if trabalhista else civel)
            break
    if peca == "Apelação" and trabalhista:
        peca = "Recurso ordinário"
    if peca == "Apelação" and juizado:
        peca, dias = "Recurso inominado", 10
    texto_prazo = prazo_no_texto(t)
    if texto_prazo and peca not in ("Apelação", "Recurso ordinário", "Recurso inominado", "Audiência designada"):
        dias = texto_prazo
    audiencia = None
    if peca == "Audiência designada":
        m = re.search(r"(\d{2}/\d{2}/\d{4})(?:[^0-9]{1,20}(\d{1,2})[:h](\d{2}))?", intim.get("texto", ""))
        if m:
            audiencia = {"data": para_data(m.group(1)).isoformat() if para_data(m.group(1)) else None,
                         "hora": f"{int(m.group(2)):02d}:{m.group(3)}" if m.group(2) else ""}
    return {"peca": peca, "dias": dias, "audiencia": audiencia, "trabalhista": trabalhista, "juizado": juizado,
            "modelo": MODELO_DA_PECA.get(peca, "Manifestação simples")}


# ───────────────────────── Modelos de petição ─────────────────────────
def ler_modelos(banco):
    """Modelos da pasta modelos/ (*.md) + os que você criou no app. Primeira linha "# Nome", segunda "prazo: N"."""
    modelos = {}
    for arq in sorted(PASTA_MODELOS.glob("*.md")):
        txt = arq.read_text(encoding="utf-8")
        linhas = txt.splitlines()
        nome = linhas[0].lstrip("# ").strip() if linhas else arq.stem
        corpo = "\n".join(linhas[1:]).lstrip("\n")
        modelos[nome] = {"texto": corpo, "proprio": False, "arquivo": arq.name}
    for nome, m in (banco.get("modelos_custom") or {}).items():
        modelos[nome] = {"texto": m.get("texto", ""), "proprio": True}
    return modelos


def campos_do_processo(banco, intim=None, proc=None, extra=None):
    cfg = banco["config"]
    proc = proc or (banco["processos"].get(intim["processo"]) if intim else None) or {}
    hoje = dt.date.today()
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
             "novembro", "dezembro"]
    oab = cfg["oabs"][0] if cfg.get("oabs") else {"numero": "[Nº]", "uf": cfg.get("uf_padrao", "PE")}
    campos = {
        "processo": proc.get("numero_fmt") or (intim or {}).get("processo_fmt") or "[Nº DO PROCESSO]",
        "orgao": (proc.get("orgao") or (intim or {}).get("orgao") or "[VARA/ÓRGÃO]").upper(),
        "tribunal": proc.get("tribunal") or (intim or {}).get("tribunal") or "",
        "classe": proc.get("classe") or (intim or {}).get("classe") or "",
        "cliente": proc.get("cliente") or "[NOME DO(A) CLIENTE]",
        "parte_contraria": proc.get("parte_contraria") or "[PARTE CONTRÁRIA]",
        "advogada": cfg.get("advogada") or "[ADVOGADA]",
        "oab": f"OAB/{oab.get('uf', 'PE')} nº {oab.get('numero', '')}",
        "escritorio": cfg.get("escritorio", ""),
        "cidade": cfg.get("cidade") or "[CIDADE]",
        "data": f"{hoje.day} de {meses[hoje.month - 1]} de {hoje.year}",
        "data_intimacao": br((intim or {}).get("data")),
        "resumo_intimacao": resumo((intim or {}).get("texto", ""), 600) or "[RESUMO DO ATO]",
    }
    campos.update(extra or {})
    return campos


def preencher(texto, campos):
    return re.sub(r"\{\{\s*(\w+)\s*\}\}", lambda m: str(campos.get(m.group(1), m.group(0))), texto)


def prompt_para_claude(intim, campos, peca, modelo_txt):
    return f"""Você é advogado(a) brasileiro(a) experiente. Redija a peça "{peca}" para o processo abaixo.

DADOS DO PROCESSO
- Processo: {campos['processo']} ({campos['tribunal']} · {campos['orgao']})
- Classe: {campos['classe']}
- Cliente (representado pela {campos['escritorio']}): {campos['cliente']}
- Parte contrária: {campos['parte_contraria']}
- Advogada: {campos['advogada']} · {campos['oab']}

INTIMAÇÃO PUBLICADA NO DJEN EM {campos['data_intimacao']}
\"\"\"
{(intim or {}).get('texto', '').strip()}
\"\"\"

MODELO DO ESCRITÓRIO (siga a estrutura)
\"\"\"
{modelo_txt.strip()}
\"\"\"

REGRAS
1. Cite apenas artigos de lei, súmulas e teses que você tem certeza de que existem; não invente julgados nem números.
2. Onde faltar um fato que só o escritório sabe, escreva [COMPLETAR: o que falta].
3. Linguagem formal, objetiva, parágrafos curtos, pedidos numerados.
4. No fim, liste em 3 linhas o que eu preciso conferir antes de protocolar (prazo, documentos, custas)."""


def gerar_docx(titulo, texto):
    """Gera o .docx da petição (Times New Roman 12, justificado). Devolve bytes."""
    from io import BytesIO

    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Pt

    doc = Document()
    for sec in doc.sections:
        sec.top_margin, sec.bottom_margin, sec.left_margin, sec.right_margin = Cm(3), Cm(2), Cm(3), Cm(2)
    estilo = doc.styles["Normal"]
    estilo.font.name, estilo.font.size = "Times New Roman", Pt(12)
    for linha in texto.splitlines():
        limpa = linha.strip()
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(6)
        negrito = limpa.startswith("**") and limpa.endswith("**") and len(limpa) > 4
        if limpa.startswith("#"):
            limpa, negrito = limpa.lstrip("# ").strip(), True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif limpa.isupper() and len(limpa) < 160:
            negrito = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if len(limpa) < 70 else WD_ALIGN_PARAGRAPH.JUSTIFY
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            if limpa:
                p.paragraph_format.first_line_indent = Cm(2)
        r = p.add_run(limpa.strip("*") if negrito else limpa)
        r.bold = negrito
    buf = BytesIO()
    doc.core_properties.title = titulo
    doc.save(buf)
    return buf.getvalue()
