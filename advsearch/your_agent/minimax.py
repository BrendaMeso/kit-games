import random
from typing import Tuple, Callable



def minimax_move(state, max_depth:int, eval_func:Callable) -> Tuple[int, int]:
    """
    Returns a move computed by the minimax algorithm with alpha-beta pruning for the given game state.
    :param state: state to make the move (instance of GameState)
    :param max_depth: maximum depth of search (-1 = unlimited)
    :param eval_func: the function to evaluate a terminal or leaf state (when search is interrupted at max_depth)
                    This function should take a GameState object and a string identifying the player,
                    and should return a float value representing the utility of the state for the player.
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """

    root_player = state.player

    def reached_depth_limit(depth):
        """
        Verifica se a busca chegou na profundidade máxima.
        Se max_depth == -1, não há limite de profundidade.
        """
        return max_depth != -1 and depth >= max_depth

    def alphabeta(current_state, depth, alpha, beta):
        """
        Calcula o valor minimax de um estado usando poda alfa-beta.
        """

        # Caso base:
        # se o jogo acabou ou chegamos na profundidade máxima,
        # usamos a função de avaliação.
        if current_state.is_terminal() or reached_depth_limit(depth):
            return eval_func(current_state, root_player)

        moves = current_state.legal_moves()

        # Segurança: se não houver jogadas, avalia o estado.
        if not moves:
            return eval_func(current_state, root_player)

        # Se é a vez do jogador da raiz, este é um nó MAX.
        if current_state.player == root_player:
            value = float("-inf")

            for move in moves:
                successor = current_state.next_state(move)
                value = max(
                    value,
                    alphabeta(successor, depth + 1, alpha, beta)
                )

                alpha = max(alpha, value)

                # Poda beta:
                # MIN já tem uma opção melhor antes, então não precisa continuar.
                if alpha >= beta:
                    break

            return value

        # Caso contrário, é a vez do adversário: nó MIN.
        else:
            value = float("inf")

            for move in moves:
                successor = current_state.next_state(move)
                value = min(
                    value,
                    alphabeta(successor, depth + 1, alpha, beta)
                )

                beta = min(beta, value)

                # Poda alfa:
                # MAX já tem uma opção melhor antes, então não precisa continuar.
                if alpha >= beta:
                    break

            return value

    best_move = None
    best_value = float("-inf")
    alpha = float("-inf")
    beta = float("inf")

    # A raiz é sempre uma decisão para o jogador atual,
    # então queremos a jogada com maior valor.
    for move in state.legal_moves():
        successor = state.next_state(move)
        value = alphabeta(successor, 1, alpha, beta)

        if value > best_value:
            best_value = value
            best_move = move

        alpha = max(alpha, best_value)

    return best_move  # = (col, row) tuple 