# py server.py othello advsearch/randomplayer/agent.py  advsearch/inf_divxs/othello_mcts.py -d 5 -p 0.5
import random
import math
import time
from typing import Tuple

# Voce pode criar funcoes auxiliares neste arquivo
# e tambem modulos auxiliares neste pacote.
#
# Nao esqueca de renomear 'inf_divxs' com o nome
# do seu agente.

"""
    Returns a move for the given game state. 
    The game is not specified, but this is MCTS and should handle any game, since
    their implementation has the same interface.

    :param state: state to make the move
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """


class MCTSNode:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move

        self.children = []
        
        if state.is_terminal():  # se o estado é terminal, não há jogadas para expandir
            self.untried_moves = []
        else:
            self.untried_moves = list(state.legal_moves()) # jogadas ainda não testadas a partir deste estado
        
        self.visits = 0
        self.wins = 0.0

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, exploration_weight=1.41):
        """
        Escolhe o filho com maior valor UCB1.

        UCB1 = taxa de vitória + exploração

        taxa de vitória = wins / visits
        exploração = c * sqrt(log(visitas_pai) / visitas_filho)
        """
        best_score = float("-inf")
        best_child = None

        for child in self.children:
            if child.visits == 0:
                return child

            exploitation = child.wins / child.visits
            exploration = exploration_weight * math.sqrt(
                math.log(self.visits) / child.visits
            )

            score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def expand(self):
        """
        Escolhe uma jogada ainda não testada,
        gera o estado sucessor e cria um novo nó filho.
        """
        move = self.untried_moves.pop()
        next_state = self.state.next_state(move)

        child = MCTSNode(
            state=next_state,
            parent=self,
            move=move
        )

        self.children.append(child)
        return child

    def update(self, result):
        """
        Atualiza estatísticas do nó.
        result é a pontuação do resultado final do ponto de vista do jogador raiz.
        """
        self.visits += 1
        self.wins += result


def rollout(state, root_player):
    """
    Simula uma partida aleatória a partir de um estado até o fim.
    Retorna:
      1.0 se root_player venceu
      0.5 se empatou
      0.0 se root_player perdeu
    """

    current_state = state

    while not current_state.is_terminal():
        moves = list(current_state.legal_moves())

        if not moves:
            break

        move = random.choice(moves)
        current_state = current_state.next_state(move)

    winner = current_state.winner()

    if winner == root_player:
        return 1.0
    elif winner is None:
        return 0.5
    else:
        return 0.0


def make_move(state) -> Tuple[int, int]:
    """
    Returns a move for the given game state.

    Implementação genérica de MCTS:
    - funciona para ambos os jogos, desde que usem a mesma interface;
    - recebe um estado;
    - retorna uma jogada no formato (x, y), isto é, (coluna, linha).
    """

    legal_moves = list(state.legal_moves())

    if not legal_moves:
        return (-1, -1)

    if len(legal_moves) == 1:
        return legal_moves[0]

    root_player = state.player
    root = MCTSNode(state)

    # Tempo máximo de busca por jogada.
    # Pode ajustar conforme o delay usado no servidor.
    time_limit = 1.0
    start_time = time.time()

    while time.time() - start_time < time_limit:
        node = root

        # 1. Seleção:
        # Desce pela árvore escolhendo filhos promissores.
        while (
            not node.state.is_terminal()
            and node.is_fully_expanded()
            and node.children
        ):
            node = node.best_child()

        # 2. Expansão:
        # Se ainda existem jogadas não testadas, cria um novo filho.
        if not node.state.is_terminal() and node.untried_moves:
            node = node.expand()

        # 3. Simulação:
        # Joga aleatoriamente até o fim.
        result = rollout(node.state, root_player)

        # 4. Retropropagação:
        # Sobe atualizando visitas e vitórias.
        while node is not None:
            node.update(result)
            node = node.parent

    # Escolhe a jogada do filho mais visitado.
    # Isso costuma ser mais estável do que escolher pela maior taxa de vitória.
    best_child = max(root.children, key=lambda child: child.visits)

    return best_child.move
