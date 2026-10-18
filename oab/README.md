# Dashboard de Estudos · 48º Exame de Ordem (OAB · FGV)

Painel da **Avany** em Streamlit para acompanhar o edital verticalizado da 1ª fase do 48º Exame de Ordem.
Visual branco e azul, com menu lateral preto, busca de tópicos no topo e cartões (horas de estudo, situação do edital, plano de hoje com a semana e progresso por matéria).

- 1ª fase: 10/01/2027 · 2ª fase: 28/02/2027 (dá para mudar em "Metas e arquivo").
- Meta: 40 de 80 acertos.

## Como abrir (Windows)
Abra a pasta `oab`, digite `cmd` na barra de endereço e aperte Enter. No Prompt de Comando, rode:

```
pip install -r requirements.txt
streamlit run app.py
```

O primeiro comando só precisa rodar uma vez.

## O que tem aqui
- `app.py`: o dashboard.
- `EDITAL OAB 48.xlsx`: o edital verticalizado. O app grava nele o progresso de cada tópico e cria as abas
  `Registro_Estudos` (pomodoros), `Plano_Diario` (caixas do Plano de hoje), `Simulados` e `Config_App`.
  O "Plano de hoje" vem do cronograma semanal da aba "Painel e Cronograma".
- `base_estudos/`: resumos e flashcards por matéria (`.md`), palavras-chave e como a FGV cobra (`analise_banca.md`)
  e as suas anotações (`anotacoes.json`).
- `materiais/`: PDFs do curso. Ficam só no computador e não vão para o GitHub. Ponha o código do tópico no nome
  do arquivo (ex.: `ETI.04 Honorários.pdf`) para ele aparecer sozinho no tópico.

Os resumos são material de apoio. Confira sempre na lei seca, nas súmulas e no edital.

## Versão online (Streamlit Community Cloud)
Crie um app novo apontando para este repositório, branch `main`, arquivo `oab/app.py`.
Em Settings > Secrets, cole o mesmo token do outro dashboard:

```
[github]
token = "seu_token"
```

Com isso a planilha e as anotações são salvas no branch `dados`, dentro da pasta `oab`, sem misturar com o dashboard da PMPE/PCPE.
