# RELATÓRIO TRABALHO 4 - BUSCA COM ADVERSÁRIO

 Brenda Melo Soares - 00587730
 Lauren Lázaro - 00179051
 Melchior Boaretto Neto - 00587628
 (Turma A)

ESTRUTURA DOS ARQUIVOS

```text
Inf-Divxs <-- diretorio na raiz do .zip
|-- __init__.py
|-- mcts.py <-- implementação do MCTS 
|-- minimax.py <-- implementação da poda alfa-beta
|-- othello_minimax_count.py <-- heuristica de contagem
|-- othello_minimax_custom.py <-- heuristica customizada
|-- othello_minimax_mask.py <-- heuristica posicional
|-- tournament_agent.py <-- melhor agente pro torneio de Othello (não preenchido ainda)
|-- tttm_minimax.py <-- minimax que joga o tic-tac-toe misere
|-- Readme.md <-- com seu relatório
|-- othello_mcts.py <-- MCTS que joga Othello 
|-- tttm_mcts.py <-- MCTS que joga tic-tac-toe misere
\-- othello_utils.py <-- métricas e operações reutilizáveis para avaliação heurística de estados de Othello  

```  

A implementação foi desenvolvida em Python utilizando apenas bibliotecas padrão da linguagem. Não foi necessária a instalação de bibliotecas externas.

TIC-TAC-TOE MISERE

```text
python test_minimax_tttm.py

....
----------------------------------------------------------------------
Ran 4 tests in 0.099s
```

Desempenho da implementação do minimax com poda alfa-beta: 
Foram realizados 10 testes para cada item. Além disso, alternamos a ordem dos jogadores “player 1” e “player 2” nos testes (i) e (iii) para verificar que os resultados apresentariam o mesmo padrão, ou seja, a ordem não afetaria significativamente o comportamento do agente. 

(i) O minimax sempre ganha ou empata jogando contra o randomplayer?
py server.py tttm advsearch/your_agent/tttm_minimax.py advsearch/randomplayer/agent.py 

Sim, houve vitória do minimax em 80% dos testes (20% de empate).

(ii) O minimax sempre empata consigo mesmo?
py server.py tttm advsearch/your_agent/tttm_minimax.py advsearch/your_agent/tttm_minimax.py

Sim, empate em 100% dos testes.

(iii) O minimax não perde para você quando você usa a sua melhor estratégia?
py server.py tttm advsearch/humanplayer/agent.py advsearch/your_agent/tttm_minimax.py

O minimax não perde para o jogador humano. 
Houve vitória do minimax em 70% dos testes (30% de empate).

Para esse teste especificamente, foi feita uma pesquisa em relação às estratégias de jogo. Quando o human_player começa jogando, constatamos que a melhor estratégia é a  primeira jogada ser no centro do tabuleiro, pois essa posição pertence a mais combinações de linhas, colunas e diagonais, aumentando o controle sobre o tabuleiro e reduzindo algumas possibilidades de armadilhas imediatas.

Os resultados sugerem que a implementação consegue explorar corretamente os estados do jogo até a profundidade terminal, tomando decisões consistentes e evitando jogadas que levariam à derrota quando existe uma alternativa segura disponível.


OTHELLO<br>

TESTAR COM  py server.py othello advsearch/your_agent/othello_minimax_custom.py advsearch/randomplayer/agent.py -d 5 <br>  
   
A heurística customizada implementada para o Othello foi baseada em uma combinação linear de resultados, ou seja, uma soma ponderada de métricas estratégicas do jogo. A ideia principal foi construir uma função de avaliação mais dinâmica do que simplesmente considerar a quantidade de peças no tabuleiro.
Para desenvolvê-la, combinamos ideias clássicas utilizadas em agentes de Othello, juntamente a adaptações e a métricas adicionais experimentais.
O objetivo principal dessa abordagem é tornar a avaliação mais próxima do raciocínio estratégico humano, equilibrando fatores como mobilidade, estabilidade, controle territorial e vulnerabilidade estrutural. A função segue também a lógica clássica de jogos de soma-zero: valores positivos representam posições favoráveis ao jogador avaliado, enquanto valores negativos representam desvantagens ou penalidades estruturais.


ADAPTAÇÃO baseada em FASES<br>
Além disso, foram utilizados pesos dinâmicos que dependem da fase da partida - o que deixou a heurística menos rígida e mais adaptada ao contexto do jogo.

A prioridade de cada métrica varia conforme a etapa da partida:
Início do jogo: mobilidade, flexibilidade e evitar vulnerabilidade
Meio do jogo: equilíbrio entre mobilidade e consolidação estrutural
Final do jogo: maximizar peças e consolidar posições estáveis

Essa ideia foi motivada pela observação de que, em Othello, possuir mais peças no início da partida nem sempre representa vantagem estratégica - ideia que será justificada na explicação das métricas.

FONTES<br>
Uma das principais referências utilizadas foi o material disponível em:<br>
http://home.datacomm.ch/t_wolf/tw/misc/reversi/html/index.html

Além do seguinte artigo:<br>
Sannidhanam, V. and Annamalai, M., 2004. An analysis of heuristics in othello. Muthukaruppan," An Analysis of Heuristics in Othello. 

A partir dessa referência, foi incorporada a ideia de que a métrica de contagem de peças (“coin parity”) deve receber maior importância apenas no final da partida. Essa observação também explica a utilização de pesos dinâmicos para outras métricas da heurística.

Isto é, a heurística não foi baseada em apenas uma única fonte. A ideia de mobilidade, mobilidade potencial, estabilidade e controle de cantos é amplamente discutida na literatura de Othello. Enquanto a proposta de utilizar pesos dinâmicos para múltiplas métricas e a métrica experimental de “controle estrutural de linhas” foram adaptações próprias desenvolvidas sobre essas ideias.<br>
DIFERENÇA DE PEÇAS (piece_diff)<br>
A primeira métrica utilizada é a que mede quantas peças o jogador possui em relação ao adversário: piece_diff = player_count - adversary_count

Embora intuitiva, possui baixa relevância estratégica no início da partida, pois em Othello muitas peças podem representar exposição excessiva e perda de mobilidade. Por isso, seu peso é pequeno no início do jogo e aumenta progressivamente no final, momento em que a quantidade de peças passa a ser realmente decisiva para a vitória.

VALOR POSICIONAL (positional_score)<br>
Conforme indicado, também foi utilizada uma máscara de valor posicional (EVAL_TEMPLATE), baseada na ideia clássica de que determinadas regiões do tabuleiro possuem importância estratégica diferente. Mede, portanto, qualidade posicional, e não apenas quantidade de peças.
Os cantos recebem valores altos, pois normalmente representam posições estáveis e difíceis de serem revertidas. Já as casas adjacentes a cantos vazios recebem penalizações, já que podem facilitar a captura futura desses cantos pelo adversário.

MOBILIDADE (mobility_score)<br>
A heurística também considera mobilidade, medida pela diferença entre a quantidade de jogadas legais disponíveis para o jogador e para o adversário (player_moves - adversary_moves).
É uma das mais importantes no Othello, pois jogadores com maior mobilidade possuem mais liberdade estratégica e maior capacidade de controlar o ritmo da partida.

Além da mobilidade imediata, foi implementada uma estimativa de mobilidade potencial, baseada na quantidade de casas vazias adjacentes às peças adversárias. A ideia é estimar oportunidades futuras de expansão e possíveis jogadas disponíveis em estados posteriores do jogo.

CANTOS (corner_score e corner_danger_score)<br>
O controle de cantos também tem um papel essencial na avaliação. Peças posicionadas nos cantos tendem a ser extremamente vantajosas, pois não podem mais ser capturadas durante a partida. Os cantos também geralmente estabilizam regiões inteiras do tabuleiro, permitindo construir bordas mais seguras. É medida a diferença entre a quantidade de cantos ocupados pelo jogador e pelo adversário, atribuindo peso elevado a essa vantagem estrutural.

Em relação aos cantos, foi considerado também o perigo próximo. Essa métrica penaliza peças localizadas nas casas adjacentes a cantos ainda vazios — conhecidas classicamente como “X-squares” e “C-squares”. Essas posições são perigosas porque frequentemente permitem ao adversário capturar o canto na jogada seguinte. Assim, a heurística mede o risco relativo de o jogador entregar cantos importantes ao adversário.

PEÇAS DE FRONTEIRA (frontier_discs)<br>
São peças adjacentes a pelo menos uma casa vazia. Em geral, são consideradas vulneráveis porque podem ser facilmente capturadas em jogadas futuras. 
Diferentemente da heurística de perigo de cantos (local e focada apenas nas regiões dos cantos) essa mede vulnerabilidade estrutural global em todo o tabuleiro. Quanto maior a quantidade de peças de fronteira do jogador, pior tende a ser sua estabilidade posicional.


ESTABILIDADE (stable_edge_discs_from_corners)<br>
É um conceito clássico de Othello que mede o quão difícil é capturar determinadas peças futuramente. Consideramos principalmente estabilidade em bordas conectadas a cantos ocupados. Por exemplo, se um canto pertence ao jogador e existem peças contínuas conectadas a ele ao longo da borda, essas peças tendem a ser muito difíceis de inverter depois. Assim, a heurística estima estabilidade estrutural sem realizar análises extremamente complexas do tabuleiro completo.


ORIGINAL (line_control_score)<br>
Por fim, foi implementada uma métrica cuja ideia é estimar um tipo de “controle estrutural” ou coerência territorial do tabuleiro, identificando regiões potencialmente favoráveis para expansão futura (por serem pouco contestadas). 

potential_line_score = line_control_score(board, player, adversary)

Basicamente, procura identificar linhas, colunas e diagonais contendo apenas peças de um jogador e espaços vazios, sem interferência do adversário. Essa métrica, diferente das anteriores, não é amplamente encontrada na literatura tradicional de estudos sobre Othello, ou seja, é uma tentativa própria de incorporar uma noção simples de controle territorial. 
Como se trata de uma métrica mais experimental, foi utilizado um peso pequeno para evitar que ela dominasse a avaliação total.


De forma geral, a heurística customizada busca combinar fatores táticos imediatos e aspectos estratégicos de longo prazo, produzindo uma avaliação mais robusta do estado do jogo do que abordagens baseadas apenas em contagem de peças. 

Formalmente, a função heurística h(s), onde s representa um estado do jogo, é definida como:

h(s) = w_p·P(s) + Pos(s) + w_m·M(s) + w_pm·PM(s) <br>
       + 30·C(s) - 12·D(s) - 4·F(s) <br>
       + w_s·S(s) + 0.5·L(s)

Onde:

- w_p: peso da diferença de peças;
- w_m: peso da mobilidade;
- w_pm: peso da mobilidade potencial;
- w_s: peso da estabilidade;
- P(s): diferença de peças;
- Pos(s): valor posicional;
- M(s): mobilidade;
- PM(s): mobilidade potencial;
- C(s): controle de cantos;
- D(s): risco próximo aos cantos;
- F(s): frontier discs;
- S(s): estabilidade;
- L(s): controle estrutural de linhas, colunas e diagonais.



CRITÉRIOS DE PARADA DO AGENTE<br>

PROFUNDIDADE MÁXIMA DINÂMICA

O critério de parada utilizado no agente baseado em minimax com poda alfa-beta foi profundidade máxima dinâmica, ajustada conforme a complexidade estimada do estado atual do jogo.

Como o custo da busca cresce exponencialmente em relação ao fator de ramificação (aproximadamente b^d, onde b representa o número médio de jogadas possíveis e d a profundidade da busca), estados com menos jogadas legais permitem buscas mais profundas sem aumento excessivo do custo computacional.

Dessa forma, a profundidade da busca foi adaptada dinamicamente de acordo com a quantidade de casas vazias e a mobilidade disponível no estado atual. Em situações de final de jogo, quando há menos espaços vazios no tabuleiro, o agente utiliza profundidade máxima maior, pois o fator de ramificação tende a ser menor. De maneira análoga, estados com poucas jogadas legais também permitem aprofundamento adicional da busca.

Na implementação em othello_minimax_custom.py , foram definidos os seguintes critérios:

- profundidade 6 para estados com menos de 12 casas vazias;
- profundidade 5 para estados com até 5 jogadas legais;
- profundidade 4 nos demais casos.

Essa estratégia busca equilibrar qualidade das decisões e custo computacional, permitindo buscas mais profundas em estados menos complexos.


TEMPORIZAÇÃO

O critério de parada utilizado, visando principalmente o torneio, foi contar até pouco antes de 5 segundos (4.85s é o ideal, 4.5s fica folgado o bastante)
e parar em tempo de retornar à execução do jogo sem extrapolar o tempo.
Além disso, foi implementada uma variação que, para toda rodada, mede o desempenho médio por nodo explorado no primeiro nível e adapta o tempo máximo para
o resto.

Para que essa estratégia funcione, é necessário guardar o melhor resultado do nível anterior ao que está sendo explorado. Tendo em vista que um timeout
invalida o que foi feito no nível atual e retornaria uma jogada ruim.

Esse [video](https://youtu.be/FSP7fBCSBl8) ilustra como o agente com mais tempo para pensar sempre ganha do que pensa por uma fração de segundo.


EXTRAS<br>
Implementação do MCTS (Monte Carlo Tree Search) - alternativa ao agente baseado em minimax com poda alfa-beta. O algoritmo foi implementado de forma genérica, dessa forma utilizado tanto no Othello quanto no Tic-Tac-Toe Misère, já que ambos os jogos utilizam a mesma interface de estados e importam funções do mcts.py
O MCTS foi estruturado seguindo as quatro etapas clássicas do algoritmo:
Seleção: os nós mais promissores da árvore são escolhidos utilizando a fórmula UCB1, que busca equilibrar a exploração de novas possibilidades e aproveitamento de jogadas com bons resultados anteriores
Expansão: novos nós são expandidos a partir de jogadas ainda não exploradas. 
Simulação: após a expansão, é realizada uma simulação aleatória da partida até um estado terminal
Retropropagação: o resultado obtido é retropropagado pela árvore para atualizar as estatísticas de visitas e vitórias dos nós percorridos

Logo, o MCTS utiliza simulação ao invés de estimação.
O critério de parada utilizado foi limite de tempo por jogada, permitindo que o algoritmo executasse o maior número possível de iterações dentro do tempo disponível. Ao final da busca, a jogada escolhida corresponde ao nó filho mais visitado da raiz, estratégia que tende a gerar decisões mais estáveis do que selecionar apenas a maior taxa de vitória observada.


MINI-TORNEIO ALGORITMOS (MINIMAX COM AS 3 HEURÍSTICAS)

Contagem de peças X Valor posicional: 35 x 29
Valor posicional X Contagem de peças: 32 x 32
Contagem de peças X Heurística customizada: 20 x 44
Heurística customizada X Contagem de peças: 50 x 14
Valor posicional X Heurística customizada: 14 x 50
Heurística customizada X Valor posicional: 50 x 14

Contagem de peças X MCTS: 26 x 38
MCTS X Contagem de peças: 41 x 23
Valor Posicional X MCTS: 19 x 45
MCTS X Valor Posicional: 23 x 41
Heurística customizada X MCTS: 47 x 17
MCTS X Heurística customizada: 19 x 45

Considerando todas as partidas realizadas, incluindo os confrontos opcionais com MCTS, a implementação melhor sucedida foi a heurística customizada.
Ela obteve 6 vitórias em 6 partidas contra os agentes minimax tradicionais (contagem de peças e valor posicional) e venceu os dois confrontos contra o agente MCTS. Além disso, foi a implementação que capturou a maior quantidade total de peças ao longo das partidas, frequentemente encerrando os jogos com ampla vantagem no placar (por exemplo, 50 x 14 e 47 x 17).




