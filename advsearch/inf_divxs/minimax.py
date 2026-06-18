import random
import time
from typing import Tuple, Callable

# Esse valor determina o quão medroso de um timeout o algoritmo deve ser.
# Pelos meus testes, 2.0 é ULTRA-FOLGADO. O que da pra fazer é tentar apertar
# mais pra explorar ainda mais nodos e tentar fechar um nivel a mais antes do timeout
FATOR_MEDO = 2.0
PERIODO_MAXIMO = 4.75
PERIODO_MINIMO = 3.0

class TimeoutException(Exception):
    pass


class TimeData:
    def __init__(self):

        self.time_limit = 4.5
        self.is_calibrated = False
        self.node_average = 0.0

    def compute_limit(self, check_interval):

        return 5.0 - (FATOR_MEDO * check_interval * self.node_average)



def minimax_move(state, max_depth: int, eval_func: Callable) -> Tuple[int, int]:
    """
    Returns a move computed by the minimax algorithm with alpha-beta pruning for the given game state.
    :param state: state to make the move (instance of GameState)
    :param max_depth: maximum depth of search (-1 = unlimited)
    :param eval_func: the function to evaluate a terminal or leaf state (when search is interrupted at max_depth)
                    This function should take a GameState object and a string identifying the player,
                    and should return a float value representing the utility of the state for the player.
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """

    # Aqui é pra contar o tempo de execução.
    # Esse time_limit inicial é arbitrário com bastante folga pra funcionar
    # em hardware bem fraco.
    #
    # O tempo total que ele computa, portanto, é t = 5s - margem.
    # Essa margem foi colocada como pT * delta_t * FATOR_MEDO
    # pT = periodo entre checks de timeout,
    # delta_t = tempo medio atual
    start_time = time.perf_counter()

    time_data = TimeData()
    node_count = [0]
    check_interval = 512

    root_player = state.player

    def order_moves(moves_list, current_state):

        if len(moves_list) <= 1:
            return moves_list

        # O reverse ali funciona pra ordenar em ordem decrescente
        return sorted(moves_list, key=lambda m: eval_func(current_state.next_state(m), root_player), reverse=True)

    def reached_depth_limit(depth, current_target_depth):
        """
        Verifica se a busca chegou na profundidade máxima.
        Se max_depth == -1, não há limite de profundidade.
        """
        return current_target_depth != -1 and depth >= current_target_depth

    def alphabeta(current_state, depth, alpha, beta, current_target_depth):
        """
        Calcula o valor minimax de um estado usando poda alfa-beta.
        """
        node_count[0] += 1

        # Verificação de timeout (pedi pro chatgpt colocar uns prints bonitinhos pra dar noção do tempo)
        if node_count[0] % check_interval == 0:
            elapsed_time = time.perf_counter() - start_time

            # Print 1
            # print(f"\r[Minimax] Profundidade Alvo: {current_target_depth} | Nodos: {node_count[0]} | Limite: {time_data.time_limit:.2f}s | Decorrido: {elapsed_time:.2f}s", end="", flush=True)

            if elapsed_time > time_data.time_limit:

                # Print 2
                # print(f"\n[Timeout] Limite de {time_data.time_limit:.4f}s atingido na Profundidade {current_target_depth}! Interrompendo recursão...")
                raise TimeoutException()

        # Caso base:
        # se o jogo acabou ou chegamos na profundidade máxima,
        # usamos a função de avaliação que ira decidir o valor do estado para o jogador da raiz 
        if current_state.is_terminal() or reached_depth_limit(depth, current_target_depth):
            return eval_func(current_state, root_player)

        moves = current_state.legal_moves()

        # Segurança: se não houver jogadas, avalia o estado, 
        # mas em teoria GameState.is_terminal() deveria sempre ser True nesse caso, então não deveríamos chegar aqui.
        if not moves:
            return eval_func(current_state, root_player)

        # Se é a vez do jogador da raiz, este é um nó MAX.
        if current_state.player == root_player:
            value = float("-inf")

            for move in moves:
                successor = current_state.next_state(move)
                value = max(
                    value,
                    alphabeta(successor, depth + 1, alpha, beta, current_target_depth)
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
                    alphabeta(successor, depth + 1, alpha, beta, current_target_depth)
                )

                beta = min(beta, value)

                # Poda alfa:
                # MAX já tem uma opção melhor antes, então não precisa continuar.
                if alpha >= beta:
                    break

            return value

    legal_moves_root = list(state.legal_moves())
    if not legal_moves_root:
        return (-1, -1)

    best_move = sorted(legal_moves_root)[0]
    actual_max_depth = max_depth if max_depth != -1 else 64

    for current_iteration_depth in range(1, actual_max_depth + 1):
        try:
            current_best_move = None
            best_value = float("-inf")
            alpha = float("-inf")
            beta = float("inf")

            # A raiz é sempre uma decisão para o jogador atual,
            # então queremos a jogada com maior valor.
            for move in order_moves(legal_moves_root, state):
                successor = state.next_state(move)
                value = alphabeta(successor, 1, alpha, beta, current_iteration_depth)

                if value > best_value:
                    best_value = value
                    current_best_move = move

                alpha = max(alpha, best_value)
            
            if current_best_move is not None:
                best_move = current_best_move

            # Aqui vai calibrar o parametro de tempo pro resto da jogada
            # dada a performance da primeira passada.
            if not time_data.is_calibrated and node_count[0] > 0:
                total_initial_time = time.perf_counter() - start_time
                time_data.node_average = total_initial_time / node_count[0]
                
                computed_limit = time_data.compute_limit(check_interval)
                time_data.time_limit = max(PERIODO_MINIMO, min(computed_limit, PERIODO_MAXIMO))
                time_data.is_calibrated = True

        except TimeoutException:
            break

    # Print 3
    # print()
    minimax_move.last_node_count = node_count[0]
    return best_move
