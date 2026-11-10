# Painel CSA ADVOCACIA

Dashboard do escritório: intimações do dia, processos (meu patrocínio e parcerias), prazos, agenda, tarefas,
modelos de petição e rascunho de petição gerado a partir de cada intimação.

## De onde vêm as intimações
Do **Diário de Justiça Eletrônico Nacional (DJEN)**, do CNJ: a mesma base em que os tribunais publicam as
intimações dirigidas aos advogados. A pesquisa pelo número da OAB é pública (https://comunica.pje.jus.br) e
não pede senha nem certificado. O app consulta pelas OABs cadastradas em ⚙️ Configurações:
- **suas OABs** → os processos entram em "Meu patrocínio";
- **OABs de parceiros** → os processos entram em "Parcerias".

Intimações que só aparecem na aba "Expedientes" do PJe (sem publicação no DJEN) não chegam por aqui:
continue de olho no painel do PJe para elas.

## Como abrir (no seu computador)
1. Abra a pasta `escritorio`, clique na barra de endereço, digite `cmd` e Enter.
2. Só na primeira vez: `pip install -r requirements.txt`
3. Para abrir: `streamlit run app.py` (ou dois cliques em `abrir_painel.bat`).
4. Em ⚙️ Configurações, cadastre o número da sua OAB e a UF e clique em Salvar.

## Busca automática todo dia
- Ao abrir, o app busca sozinho se ainda não buscou no dia.
- Para buscar mesmo com o app fechado: dois cliques em `agendar_captura.bat` (uma vez só). O Windows passa a
  rodar `capturar.py` todo dia às 07:30 e às 13:30. O resultado fica em `captura.log`.

## Prazos
Contagem em dias úteis: publicação no 1º dia útil após a disponibilização no DJEN e início no dia útil seguinte
(Lei 11.419/2006, art. 4º; CPC, arts. 219 e 224), com suspensão de 20/12 a 20/01 (CPC, art. 220). Feriados
locais e portarias do tribunal você cadastra em Configurações. **O cálculo é uma ajuda: confira sempre.**

## Petições
- `modelos/*.md`: modelos padrão (primeira linha `# Nome do modelo`). Campos `{{processo}}`, `{{orgao}}`,
  `{{cliente}}`, `{{parte_contraria}}`, `{{advogada}}`, `{{oab}}`, `{{cidade}}`, `{{data}}`, `{{data_intimacao}}`,
  `{{resumo_intimacao}}` são preenchidos sozinhos.
- Em cada intimação, **📝 Gerar petição** cria o rascunho com o modelo certo; baixe em Word (.docx).
- O botão "Quer que o Claude escreva a peça completa?" monta o pedido pronto para colar no chat do Claude.

## Seus dados
Ficam em `dados/escritorio.json` (com cópia diária em `dados/backup`). Essa pasta **não vai para o GitHub**
(dados de clientes, LGPD).
