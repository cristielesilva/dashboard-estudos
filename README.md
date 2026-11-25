# Dashboard de Estudos · PMPE (Soldado e Oficial)

Painel em Streamlit para estudar para o concurso da **PMPE 2026/2027** (Edital 001/2026, banca **Instituto AOCP**, prova em **21/02/2027**): Soldado (manhã) e Oficial QOPM (tarde).

## Como abrir (Windows)
Dentro desta pasta, abra o Prompt de Comando (digite `cmd` na barra de endereço) e rode:

```
pip install -r requirements.txt
streamlit run app.py
```

O primeiro comando só precisa rodar uma vez, ou de novo quando o `requirements.txt` mudar.

## O que tem aqui
- `app.py`: o dashboard. Páginas: Início (pomodoro e plano de hoje), Estudar, Resumo do dia, **Questões** (meta por dia e por matéria, com atalhos para QConcursos e TecConcursos), Revisões e uma página para cada cargo.
- `CRONOGRAMA PMPE.xlsx`: os 139 tópicos do edital (Soldado, Oficial ou os dois), com data planejada até 26/01/2027, progresso, revisões e questões. O app grava nesta planilha.
- `cronograma - MATÉRIAS.xlsx`: fases e grade semanal usadas no "Plano de hoje".
- `base_estudos/`: resumos e flashcards (`<matéria>.md`), palavras-chave e como a AOCP cobra (`analise_banca.md`), videoaulas (`videos.json`) e suas anotações (`anotacoes.json`).
- `materiais/`: PDFs baixados do curso. Ficam só no computador e não vão para o GitHub (veja `.gitignore`).

Os resumos são material de apoio. Confira sempre na lei seca e no edital (site do Instituto AOCP).
