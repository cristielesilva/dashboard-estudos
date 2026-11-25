# Informática

Formato: cada tópico começa com "## CÓDIGO". Edite à vontade; o app lê este arquivo.

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
- P: Como buscar só PDFs no site da PMPE?
  R: site:pm.pe.gov.br filetype:pdf (mais os termos).

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

## INF-10
### Resumo
- **CPU (processador)**: Unidade de Controle (UC) coordena; Unidade Lógica e Aritmética (ULA) faz os cálculos; **registradores** são a memória mais rápida e interna.
- **Memória RAM**: principal, **volátil** (apaga ao desligar), leitura e escrita. **ROM**: não volátil, guarda o firmware (BIOS/UEFI). **Cache**: pequena e muito rápida, entre CPU e RAM.
- **Memória secundária (armazenamento)**: HD (magnético), **SSD** (flash, mais rápido e sem partes móveis), pendrive, cartão de memória.
- **Periféricos**: entrada (teclado, mouse, scanner, microfone), saída (monitor, impressora, caixa de som) e **entrada e saída** (touchscreen, impressora multifuncional, pendrive, placa de rede).
- Unidades: 1 byte = 8 bits; 1 KB = 1024 bytes; depois MB, GB e TB.
- **Arquivos e pastas**: extensão indica o tipo (.docx, .xlsx, .pdf, .exe); caminho absoluto começa na unidade (C:\Usuarios\...).
### Flashcards
- P: Qual memória é volátil: RAM ou ROM?
  R: RAM. Ela perde os dados quando o computador desliga.
- P: Touchscreen é periférico de entrada, saída ou ambos?
  R: Ambos (entrada e saída).
