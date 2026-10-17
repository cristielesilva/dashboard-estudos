# Dashboard de Estudos · PMPE & PCPE

Painel em Streamlit para acompanhar o edital da PMPE (Oficial + Soldado) e da PCPE (Agente + Escrivão).

## Como abrir (Windows)
Dentro desta pasta, abra o Prompt de Comando (digite `cmd` na barra de endereço) e rode:

```
pip install -r requirements.txt
streamlit run app.py
```

O primeiro comando só precisa rodar uma vez, ou de novo quando o `requirements.txt` mudar.

## O que tem aqui
- `app.py`: o dashboard.
- `CRONOGRAMA - ASSUNTO.xlsx`: progresso por tópico. O app grava nesta planilha.
- `cronograma - MATÉRIAS.xlsx`: grade semanal usada no "Plano de hoje".
- `base_estudos/`: resumos, flashcards (`<matéria>.md`), palavras-chave e como a banca cobra (`analise_banca.md`) e suas anotações (`anotacoes.json`).
- `materiais/`: PDFs baixados do curso. Ficam só no computador e não vão para o GitHub (veja `.gitignore`). Ponha o código do tópico no nome do arquivo (ex.: `PENAL-08 Furto e Roubo.pdf`) para ele aparecer sozinho no tópico.

Os resumos são material de apoio. Confira sempre na lei seca e no edital.
