# Informática & Arquivologia

## INF-01
### Resumo
- **Windows 11**: menu Iniciar centralizado, Widgets, Snap Layouts (organizar janelas) e áreas de trabalho virtuais.
- **Explorador de Arquivos**: Win + E. Lixeira guarda itens excluídos; **Shift + Del** exclui direto, sem passar pela Lixeira.
- Atalhos: **Win + D** (área de trabalho), **Win + L** (bloquear), **Alt + Tab** (alternar), **Ctrl + Shift + Esc** (Gerenciador de Tarefas), **Win + V** (histórico da área de transferência), **Win + Shift + S** (captura).
- Arrastar na mesma unidade **move**; para outra unidade **copia**. Ctrl + arrastar copia; Shift + arrastar move.
- Extensões comuns: .docx, .xlsx, .pdf, .exe, .zip.
### Flashcards
- P: O que faz Shift + Delete?
  R: Exclui o arquivo permanentemente, sem enviá-lo para a Lixeira.
- P: Arrastar um arquivo de C: para um pendrive faz o quê, por padrão?
  R: Copia (unidades diferentes).

## INF-02
### Resumo
- **Word**: estilos (Título 1, 2...) permitem gerar **sumário automático**.
- Atalhos: Ctrl + N (negrito), Ctrl + I (itálico), Ctrl + S (sublinhado), Ctrl + B (salvar), Ctrl + L (localizar), Ctrl + U (substituir), Ctrl + J (justificar), Ctrl + E (centralizar).
- **Quebra de página** (Ctrl + Enter) x **quebra de seção** (permite orientação e cabeçalhos diferentes).
- Margens, orientação e tamanho ficam em **Layout**. Revisão traz controle de alterações e comentários.
- **Mala direta** gera cartas personalizadas a partir de uma lista de dados.
### Flashcards
- P: Como ter páginas retrato e paisagem no mesmo documento do Word?
  R: Inserindo uma quebra de seção e configurando cada seção.
- P: Atalho para justificar texto no Word em português?
  R: Ctrl + J.

## INF-03
### Resumo
- Fórmulas começam com **=**. Referências: relativa (A1), absoluta (**$A$1**) e mista ($A1 ou A$1).
- Funções: SOMA, MÉDIA, MÁXIMO, MÍNIMO, CONT.NÚM (números), CONT.VALORES (não vazias), CONT.SE, SOMASE, SE, PROCV/PROCX, CONCATENAR e ARRED.
- **SE(teste; se_verdadeiro; se_falso)**. **PROCV(valor; matriz; coluna; 0 = exato)**.
- Erros: #DIV/0!, #N/D (não encontrado), #REF! (referência inválida), #NOME? (função escrita errada) e #VALOR!.
- Ao copiar a fórmula, as referências relativas se ajustam e o $ trava linha ou coluna.
### Flashcards
- P: Copiando =A1*$B$1 de C1 para C2, como fica?
  R: =A2*$B$1.
- P: Diferença entre CONT.NÚM e CONT.VALORES?
  R: CONT.NÚM conta só células com números; CONT.VALORES conta todas as não vazias.

## INF-04
### Resumo
- **PowerPoint**: F5 inicia a apresentação do começo e Shift + F5 inicia do slide atual. O **slide mestre** padroniza o layout.
- Diferença entre transições (entre slides) e animações (objetos dentro do slide).
- **LibreOffice**: Writer (texto), Calc (planilhas) e Impress (apresentações). O formato padrão é ODF (.odt, .ods, .odp).
- No **Calc**, funções usam ponto e vírgula, e algumas têm nomes próprios.
- Atalhos do Writer diferem: Ctrl + B negrito e Ctrl + I itálico (padrão em inglês). Ctrl + S salva.
### Flashcards
- P: Extensão padrão de planilha no LibreOffice Calc?
  R: .ods.
- P: Atalho para iniciar a apresentação a partir do slide atual no PowerPoint?
  R: Shift + F5.

## INF-05
### Resumo
- **Internet** é a rede mundial pública. **Intranet** é a rede privada que usa as mesmas tecnologias (TCP/IP, HTTP). **Extranet** é a intranet aberta a parceiros.
- Protocolos: HTTP/HTTPS (web, o S indica criptografia TLS), FTP (arquivos), SMTP (envio de e-mail), POP3/IMAP (recebimento) e DNS (nomes para IP).
- Navegadores: guia anônima/InPrivate não salva histórico local, mas não esconde de provedor ou empresa. Ctrl + Shift + N abre janela anônima no Chrome.
- **Busca avançada (Google)**: "frase exata", -excluir, site:gov.br, filetype:pdf, OR.
### Flashcards
- P: Intranet usa os mesmos protocolos da Internet?
  R: Sim (TCP/IP, HTTP), mas com acesso restrito à organização.
- P: Como buscar só PDFs no site da PCPE?
  R: site:policiacivil.pe.gov.br filetype:pdf (mais os termos).

## INF-06
### Resumo
- **Computação em nuvem**: IaaS (infraestrutura), PaaS (plataforma) e SaaS (software pronto, como Gmail e Microsoft 365).
- Modelos de nuvem: pública, privada, híbrida e comunitária.
- **Deep Web**: conteúdo não indexado por buscadores (sistemas internos, e-mails). **Dark Web**: parte da Deep Web acessível só por softwares específicos (Tor), com anonimato.
- **Redes sociais**: cuidado com engenharia social e exposição de dados.
- **Webmail**, mensageiros, armazenamento (Drive, OneDrive) e videoconferência são exemplos de serviços.
### Flashcards
- P: Gmail é exemplo de qual modelo de nuvem?
  R: SaaS (Software como Serviço).
- P: Toda Deep Web é ilegal?
  R: Não. Deep Web é apenas o conteúdo não indexado; a Dark Web é a parte que exige ferramentas como o Tor.

## INF-07
### Resumo
- Pilares: **confidencialidade, integridade, disponibilidade** (CID), além de autenticidade e não repúdio.
- **Malwares**: vírus (precisa de hospedeiro), worm (se propaga sozinho pela rede), trojan (disfarçado), ransomware (sequestra dados com criptografia), spyware/keylogger (espiona), backdoor e bot/botnet.
- **Phishing**: e-mail ou site falso para roubar dados. **Engenharia social** explora a confiança humana.
- **Criptografia simétrica** usa uma chave. A **assimétrica** usa chave pública e privada. A assinatura digital garante autenticidade e integridade.
- **Firewall** filtra o tráfego de rede. O **antivírus** detecta malware. O **2FA** reforça a autenticação.
### Flashcards
- P: Diferença entre vírus e worm?
  R: Vírus precisa de um arquivo hospedeiro e de execução; worm se replica sozinho pela rede.
- P: Na criptografia assimétrica, com qual chave se cifra para que só o destinatário leia?
  R: Com a chave pública do destinatário (ele decifra com a privada).

## INF-08
### Resumo
- **Backup completo**: copia tudo.
- **Incremental**: copia só o que mudou desde o último backup de qualquer tipo. É rápido para fazer e lento para restaurar.
- **Diferencial**: copia o que mudou desde o último backup **completo**. Cresce a cada dia e restaura mais rápido.
- **Regra 3-2-1**: 3 cópias, em 2 mídias diferentes, sendo 1 fora do local (nuvem).
- Sincronização na nuvem **não é backup**, porque a exclusão também é sincronizada.
### Flashcards
- P: Para restaurar, quais backups são necessários no esquema incremental?
  R: O último completo e todos os incrementais seguintes.
- P: E no diferencial?
  R: O último completo e o último diferencial.

## INF-09
### Resumo
- Por abrangência: **LAN** (local), **MAN** (metropolitana), **WAN** (longa distância) e **PAN** (pessoal, como Bluetooth).
- Equipamentos: **switch** (conecta dispositivos na LAN), **roteador** (interliga redes) e **modem**/ponto de acesso Wi-Fi.
- **Endereço IP** (IPv4 32 bits, IPv6 128 bits). **DHCP** atribui IP automaticamente. **DNS** traduz nomes.
- **TCP** é confiável e orientado a conexão. **UDP** é rápido e sem confirmação, usado em streaming e VoIP.
- Ferramentas de comunicação: e-mail (com CC e CCO, sendo que o CCO oculta destinatários) e videoconferência.
### Flashcards
- P: Qual protocolo atribui IP automaticamente?
  R: DHCP.
- P: No e-mail, quem está em CCO aparece para os demais destinatários?
  R: Não. A cópia oculta esconde esses endereços.

## ARQ-01
### Resumo
- **Arquivo**: conjunto de documentos produzidos e recebidos por uma instituição no exercício de suas atividades.
- **Princípio da proveniência** (respeito aos fundos): não misturar documentos de origens diferentes.
- Outros princípios: organicidade, unicidade, indivisibilidade (integridade) e cumulatividade.
- **Funções arquivísticas**: criação, avaliação, aquisição, conservação, classificação, descrição e difusão.
- **Teoria das três idades**: corrente, intermediária e permanente.
### Flashcards
- P: O que diz o princípio da proveniência?
  R: Os documentos de uma entidade devem ser mantidos juntos, sem se misturar aos de outras origens.
- P: Quais são as três idades dos documentos?
  R: Corrente (uso frequente), intermediária (uso eventual) e permanente (guarda definitiva por valor histórico).

## ARQ-02
### Resumo
- **Lei nº 8.159/1991** (Política Nacional de Arquivos): é dever do poder público a gestão documental e a proteção dos arquivos.
- **CONARQ** (Conselho Nacional de Arquivos) define a política nacional. O **SINAR** é o Sistema Nacional de Arquivos.
- Arquivos públicos x privados. Os privados podem ser declarados de **interesse público e social**.
- **Eliminação** de documentos públicos depende de autorização da instituição arquivística competente.
- Documentos de valor permanente são **inalienáveis e imprescritíveis**.
### Flashcards
- P: Qual lei institui a Política Nacional de Arquivos?
  R: Lei nº 8.159/1991.
- P: Documento público de valor permanente pode ser eliminado?
  R: Não. É inalienável e imprescritível.

## ARQ-03
### Resumo
- **Gestão de documentos**: procedimentos de produção, tramitação, uso, avaliação e arquivamento nas fases corrente e intermediária.
- **Protocolo**: recebimento, registro, classificação, distribuição, tramitação e expedição.
- **Registro**: anotar dados do documento (número, data, procedência, assunto) para controle.
- **Autuação**: transformar documentos em processo. Juntada pode ser por anexação ou apensação.
- **Tramitação**: movimentação do documento entre setores, com controle de onde ele está.
### Flashcards
- P: Diferença entre anexação e apensação?
  R: Anexação é a união definitiva de processos; apensação é a união temporária, para estudo conjunto.
- P: Qual a primeira atividade do protocolo ao receber um documento?
  R: O recebimento, seguido do registro.

## ARQ-04
### Resumo
- **Avaliação**: define prazos de guarda e destinação (eliminação ou guarda permanente) pela **Tabela de Temporalidade**.
- **Classificação**: organizar segundo o plano de classificação (por funções e atividades).
- **Ordenação** pode ser alfabética, numérica, cronológica, geográfica ou ideográfica (por assunto).
- **Arquivamento**: guardar em local e forma adequados (pastas, caixas).
- **Conservação preventiva**: controle de temperatura, umidade, luz e pragas. **Restauração** é a intervenção no documento danificado.
### Flashcards
- P: Qual instrumento define prazos de guarda e destinação?
  R: A Tabela de Temporalidade de Documentos.
- P: Método de ordenação por assunto chama-se?
  R: Ideográfico (alfabético ou numérico).

## ARQ-05
### Resumo
- **SIGAD** (Sistema Informatizado de Gestão Arquivística de Documentos) segue o modelo **e-ARQ Brasil**.
- **Documento digital**: codificado em dígitos binários e acessível por sistema computacional. **Digitalizado** é a representação digital de um documento físico.
- **Metadados**: dados sobre os dados (autor, data, formato, classificação), que garantem contexto, autenticidade e preservação.
- **RDC-Arq**: repositório digital confiável para preservação de longo prazo.
- Preservação digital envolve migração de formatos, emulação e cópias de segurança.
### Flashcards
- P: Qual o modelo de requisitos para SIGAD no Brasil?
  R: e-ARQ Brasil.
- P: O que são metadados?
  R: Informações que descrevem o documento (contexto, conteúdo, estrutura) e garantem sua gestão e autenticidade.
