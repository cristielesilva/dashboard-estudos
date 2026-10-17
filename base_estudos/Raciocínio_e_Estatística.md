# Raciocínio Lógico & Estatística

## RLM-01
### Resumo
- **Proposição** é uma frase declarativa que pode ser V ou F. Perguntas, ordens, exclamações e sentenças abertas ("x > 2") não são proposições.
- **Conectivos**: negação (~), conjunção (∧, "e"), disjunção (∨, "ou"), disjunção exclusiva (⊻, "ou... ou"), condicional (→, "se... então") e bicondicional (↔, "se e somente se").
- Na condicional p → q, p é **antecedente** (condição suficiente) e q é **consequente** (condição necessária).
- Nº de linhas da tabela-verdade = **2ⁿ**, onde n é o número de proposições simples.
### Flashcards
- P: "Que horas são?" é proposição?
  R: Não. Frases interrogativas não podem ser julgadas como V ou F.
- P: Em "Se chove, então molha", qual é a condição suficiente?
  R: "Chove" (o antecedente).

## RLM-02
### Resumo
- **E (∧)**: só é V se as duas forem V.
- **OU (∨)**: só é F se as duas forem F.
- **Se... então (→)**: só é F no caso **V → F** ("Vera Fischer").
- **Se e somente se (↔)**: V quando os valores são iguais.
- **Ou... ou (⊻)**: V quando os valores são diferentes.
- **Tautologia**: sempre V (ex.: p ∨ ~p). **Contradição**: sempre F (p ∧ ~p). **Contingência**: às vezes V, às vezes F.
### Flashcards
- P: Quando a condicional p → q é falsa?
  R: Somente quando p é verdadeira e q é falsa.
- P: p ∨ ~p é o quê?
  R: Tautologia (sempre verdadeira).

## RLM-03
### Resumo
- **Argumento** é formado por premissas e conclusão. Ele é **válido** quando, se as premissas forem verdadeiras, a conclusão obrigatoriamente também é.
- Validade depende da **forma**, não da verdade das frases.
- Método prático: considere as premissas verdadeiras e descubra os valores lógicos, começando pela proposição simples ou pela conjunção.
- **Modus ponens**: p → q; p; logo q (válido). **Modus tollens**: p → q; ~q; logo ~p (válido).
- **Falácias comuns**: afirmar o consequente (p → q; q; logo p) e negar o antecedente (p → q; ~p; logo ~q).
### Flashcards
- P: "Se estudo, passo. Passei. Logo, estudei." é válido?
  R: Não. É a falácia de afirmar o consequente.
- P: Um argumento válido pode ter conclusão falsa?
  R: Sim, se alguma premissa for falsa. A validade diz respeito apenas à forma.

## RLM-04
### Resumo
- **De Morgan**: ~(p ∧ q) ≡ ~p ∨ ~q; ~(p ∨ q) ≡ ~p ∧ ~q.
- **Negação da condicional**: ~(p → q) ≡ p ∧ ~q ("mantém a primeira E nega a segunda").
- **Equivalências da condicional**: p → q ≡ ~q → ~p (contrapositiva) ≡ ~p ∨ q ("nega a primeira OU mantém a segunda").
- p ↔ q ≡ (p → q) ∧ (q → p). Negação de p ↔ q é p ⊻ q.
- Dupla negação: ~(~p) ≡ p.
### Flashcards
- P: Negação de "Se estudo, então passo"?
  R: "Estudo e não passo".
- P: Equivalente de "Se chove, então molha" pela contrapositiva?
  R: "Se não molha, então não chove".

## RLM-05
### Resumo
- **Todo A é B**: A está contido em B. **Algum A é B**: há interseção. **Nenhum A é B**: conjuntos disjuntos.
- **Negações**: de "Todo A é B" é "Algum A não é B"; de "Algum A é B" é "Nenhum A é B"; de "Nenhum A é B" é "Algum A é B".
- Quantificador universal ∀ ("para todo") e existencial ∃ ("existe pelo menos um").
- Use **diagramas de Venn** e teste se a conclusão é obrigatória em todos os desenhos possíveis.
### Flashcards
- P: Negação de "Todos os policiais são honestos"?
  R: "Algum (pelo menos um) policial não é honesto".
- P: "Algum A é B" garante que "Algum B é A"?
  R: Sim. A interseção é simétrica.

## RLM-06
### Resumo
- **Princípio multiplicativo**: etapas sucessivas e independentes se multiplicam.
- **Permutação simples**: Pₙ = n! (ordenar todos os elementos).
- **Permutação com repetição**: n! / (a! b! ...), útil em anagramas com letras repetidas.
- **Arranjo** (a ordem importa): A(n,p) = n! / (n − p)!
- **Combinação** (a ordem não importa): C(n,p) = n! / [p! (n − p)!]
- Teste: troque a ordem dos elementos escolhidos. Se mudar o resultado, é arranjo; se não mudar, é combinação.
### Flashcards
- P: Escolher 3 pessoas de 10 para uma comissão sem cargos é arranjo ou combinação?
  R: Combinação: C(10,3) = 120.
- P: Quantos anagramas tem a palavra "ARARA"?
  R: 5! / (3! · 2!) = 10.

## RLM-07
### Resumo
- **P(A) = casos favoráveis / casos possíveis**, com valor entre 0 e 1.
- **Complementar**: P(não A) = 1 − P(A).
- **União**: P(A ∪ B) = P(A) + P(B) − P(A ∩ B).
- **Condicional**: P(A|B) = P(A ∩ B) / P(B).
- **Independentes**: P(A ∩ B) = P(A) · P(B). Use "E" para multiplicar e "OU" para somar quando os eventos são mutuamente exclusivos.
### Flashcards
- P: Probabilidade de sair pelo menos uma cara em 2 lançamentos de moeda?
  R: 1 − P(nenhuma cara) = 1 − 1/4 = 3/4.
- P: Quando dois eventos são independentes?
  R: Quando P(A ∩ B) = P(A) · P(B), ou seja, um não altera a chance do outro.

## RLM-08
### Resumo
- ℕ (naturais) ⊂ ℤ (inteiros) ⊂ ℚ (racionais) ⊂ ℝ (reais). Os irracionais (√2, π) completam os reais.
- **Racional**: pode ser escrito como fração a/b, com b ≠ 0, o que inclui as dízimas periódicas.
- **Operações**: união (∪), interseção (∩), diferença (A − B) e complementar.
- **n(A ∪ B) = n(A) + n(B) − n(A ∩ B)**. Para 3 conjuntos, use o diagrama começando pela interseção tripla.
- Nº de subconjuntos de um conjunto com n elementos = **2ⁿ**.
### Flashcards
- P: 0,333... é racional?
  R: Sim. É dízima periódica, igual a 1/3.
- P: Quantos subconjuntos tem {a, b, c}?
  R: 2³ = 8.

## RLM-09
### Resumo
- **Razão**: a/b. **Proporção**: igualdade de razões (a/b = c/d, logo a·d = b·c).
- **Divisão proporcional**: direta (partes proporcionais aos números) e inversa (proporcionais aos inversos).
- **Regra de três simples**: identifique se as grandezas são direta ou inversamente proporcionais.
- **Regra de três composta**: compare cada grandeza com a incógnita, inverta as inversas e multiplique.
- Exemplo de grandezas inversas: mais trabalhadores, menos dias.
### Flashcards
- P: 4 pedreiros fazem um muro em 6 dias. Em quantos dias 8 pedreiros fazem o mesmo muro?
  R: 3 dias (grandezas inversamente proporcionais).
- P: Divida 100 em partes diretamente proporcionais a 2 e 3.
  R: 40 e 60.

## RLM-10
### Resumo
- **Porcentagem**: x% = x/100. Aumento de i% multiplica por (1 + i); desconto de i% multiplica por (1 − i).
- **Aumentos sucessivos** se multiplicam (10% e depois 10% = 1,1 · 1,1 = 1,21, ou seja, 21%).
- **1º grau**: ax + b = 0, com raiz x = −b/a. Na inequação, ao multiplicar por número negativo, **inverta o sinal**.
- **2º grau**: Δ = b² − 4ac; x = (−b ± √Δ) / 2a. Soma das raízes = −b/a; produto = c/a.
- **Sistemas lineares**: resolva por substituição ou adição.
### Flashcards
- P: Um produto sobe 20% e depois cai 20%. Qual a variação final?
  R: 1,2 · 0,8 = 0,96, ou seja, queda de 4%.
- P: Soma e produto das raízes de x² − 5x + 6 = 0?
  R: Soma 5, produto 6 (raízes 2 e 3).

## RLM-11
### Resumo
- **PA**: aₙ = a₁ + (n − 1)·r. Soma: Sₙ = (a₁ + aₙ)·n / 2.
- **PG**: aₙ = a₁ · qⁿ⁻¹. Soma finita: Sₙ = a₁(qⁿ − 1)/(q − 1).
- **Soma da PG infinita** (para |q| < 1): S = a₁ / (1 − q).
- Termo médio: na PA é a média aritmética dos vizinhos; na PG é a média geométrica.
### Flashcards
- P: 10º termo da PA (2, 5, 8, ...)?
  R: a₁₀ = 2 + 9·3 = 29.
- P: Soma da PG infinita 1 + 1/2 + 1/4 + ...?
  R: 1 / (1 − 1/2) = 2.

## EST-01
### Resumo
- **População** é o conjunto total; **amostra** é uma parte dela.
- **Variáveis qualitativas** podem ser nominais ou ordinais. **Variáveis quantitativas** podem ser discretas (contagem) ou contínuas (medida).
- **Tabelas de frequência**: absoluta, relativa (%) e acumulada.
- **Gráficos**: barras e setores (qualitativas), histograma (quantitativa contínua), boxplot (mediana e quartis) e linhas (série temporal).
- **Histograma** mostra a forma da distribuição: simétrica ou assimétrica à direita ou à esquerda.
### Flashcards
- P: Número de filhos é variável de que tipo?
  R: Quantitativa discreta.
- P: O que o boxplot mostra?
  R: Mediana, quartis (Q1 e Q3), amplitude interquartil e possíveis valores atípicos (outliers).

## EST-02
### Resumo
- **Média** é a soma dividida por n e é sensível a valores extremos. **Mediana** é o valor central dos dados ordenados. **Moda** é o valor mais frequente.
- **Amplitude** = máximo − mínimo.
- **Variância**: média dos quadrados dos desvios. A variância amostral divide por (n − 1).
- **Desvio padrão** = √variância, na mesma unidade dos dados.
- **Coeficiente de variação** = desvio padrão / média, usado para comparar dispersões relativas.
- Somar uma constante não altera a variância. Multiplicar por k multiplica o desvio padrão por k e a variância por k².
### Flashcards
- P: Se somarmos 5 a todos os valores, o que acontece com média e desvio padrão?
  R: A média aumenta 5 e o desvio padrão não muda.
- P: Mediana de {3, 7, 1, 9}?
  R: Ordenando (1, 3, 7, 9): (3 + 7)/2 = 5.

## EST-03
### Resumo
- **Variável aleatória** associa um número a cada resultado de um experimento.
- **Discreta**: assume valores contáveis e tem função de probabilidade P(X = x).
- **Contínua**: assume valores num intervalo e tem função densidade, com P(X = x) = 0.
- **Esperança**: E(X) = Σ x·P(x). **Variância**: Var(X) = E(X²) − [E(X)]².
- Distribuições cobradas: **Binomial** (n tentativas, sucesso p: E = np, Var = np(1 − p)), **Poisson** (eventos raros, E = Var = λ) e **Normal** (simétrica, média = mediana = moda).
### Flashcards
- P: Esperança de uma binomial com n = 10 e p = 0,3?
  R: E = np = 3.
- P: Numa variável contínua, quanto vale P(X = 3)?
  R: Zero. A probabilidade é medida em intervalos.

## EST-04
### Resumo
- **Aleatória simples**: todos os elementos têm a mesma chance (sorteio).
- **Sistemática**: escolhe-se de k em k elementos de uma lista, a partir de um início aleatório.
- **Estratificada**: divide a população em estratos homogêneos e sorteia dentro de cada um, muitas vezes de forma proporcional.
- **Por conglomerados**: sorteia grupos inteiros (bairros, turmas), que são heterogêneos internamente.
- Amostragens **não probabilísticas**: por conveniência, por cotas e intencional.
### Flashcards
- P: Diferença entre estratificada e por conglomerados?
  R: Na estratificada, sorteiam-se elementos dentro de cada estrato homogêneo. Por conglomerados, sorteiam-se grupos inteiros, heterogêneos internamente.
- P: Escolher cada 10º nome de uma lista é que amostragem?
  R: Sistemática.

## EST-05
### Resumo
- **H₀** (hipótese nula) x **H₁** (alternativa). **Erro tipo I** é rejeitar H₀ verdadeira (probabilidade α). **Erro tipo II** é não rejeitar H₀ falsa (β).
- **p-valor < α**: rejeita-se H₀.
- **Teste t**: compara médias com variância desconhecida. **Teste F / ANOVA**: compara variâncias ou mais de duas médias.
- **Regressão linear**: y = a + bx. O coeficiente **b** é a inclinação. **R²** mostra a proporção da variação explicada (0 a 1).
- **Correlação de Pearson (r)**: varia de −1 a 1. Correlação não implica causalidade.
### Flashcards
- P: O que é erro tipo I?
  R: Rejeitar a hipótese nula quando ela é verdadeira (probabilidade α, nível de significância).
- P: R² = 0,81 significa?
  R: 81% da variação de y é explicada pelo modelo (|r| = 0,9).
