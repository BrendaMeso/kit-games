import random
import time
from typing import Tuple
from ..othello.gamestate import GameState
from ..othello.board import Board
from .minimax import minimax_move
import csv
from .othello_utils import (
    DIRECTIONS,
    count_pieces,
    legal_moves_count_for,
    opponent,
    get_board_matrix,
    in_bounds,
    frontier_discs,
    stable_edge_discs_from_corners,
    get_lines,
)

MAX_DEPTH = 3

EVAL_TEMPLATE = [
    [100, -30, 6, 2, 2, 6, -30, 100],
    [-30, -50, 1, 1, 1, 1, -50, -30],
    [  6,   1, 1, 1, 1, 1,   1,   6],
    [  2,   1, 1, 3, 3, 1,   1,   2],
    [  2,   1, 1, 3, 3, 1,   1,   2],
    [  6,   1, 1, 1, 1, 1,   1,   6],
    [-30, -50, 1, 1, 1, 1, -50, -30],
    [100, -30, 6, 2, 2, 6, -30, 100]
]  # máscara de valor poscional (Ex: cantos são muito bons, casas próximas a cantos vazios são ruins, etc)



TIMING_LOG = "timing_othello_custom.csv" # joga em um csv o tempo gasto em cada jogada

with open(TIMING_LOG, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "jogador",
        "quantidade_de_jogadas_legais",
        "casas_vazias",
        "tempo",
        "jogada"
    ]) # cabeçalho do csv
    
# state --> move/jogada (col, row) tuple
def make_move(state) -> Tuple[int, int]:
    legal_moves = list(state.legal_moves())

    if not legal_moves:
        return (-1, -1)

    # Usa o método get_board() oferecido pelo GameState do Othello 
    board = state.get_board()
    empty_count = board.num_pieces(Board.EMPTY)
    # numero de casas vazias no tabuleiro (estado) atual --> indica etapa do jogo
    
    start_time = time.perf_counter()

    # Chama minimax passando a função de avaliação customizada
    move = minimax_move(state, MAX_DEPTH, evaluate_custom)

    # Mede quanto tempo a função demorou para retornar a jogada
    elapsed = time.perf_counter() - start_time

    # Registra no CSV.
    with open(TIMING_LOG, "a", encoding="utf-8") as f:
        f.write(
            f"{state.player},{len(legal_moves)},{empty_count},{elapsed:.6f},{move}\n"
        )

    return move



def positional_score(board, player: str, adversary: str) -> float:
    score = 0.0
    size = len(board)
    for row in range(size):
        for col in range(size):
            cell = board[row][col]

            if cell == player:
                score += EVAL_TEMPLATE[row][col]  # continua ideia de jogo soma-zero
            elif cell == adversary:
                score -= EVAL_TEMPLATE[row][col]  # peças do adversário em posições boas para mim são ruins para mim, e vice-versa

    return score




def mobility_score(state, player: str, adversary: str) -> float:
    player_moves = legal_moves_count_for(state, player)
    adversary_moves = legal_moves_count_for(state, adversary)

    return float(player_moves - adversary_moves) # (minhas jogadas possiveis) - (jogadas possiveis do adversario)


def potential_mobility(board, player: str, adversary: str) -> int:
    """
    Conta casas vazias adjacentes a peças do adversário.
    Isso aproxima quantas oportunidades futuras o jogador pode ter.
    """

    size = len(board)
    potential_squares = set()

    for row in range(size):
        for col in range(size):
            if board[row][col] == adversary:
                for dr, dc in DIRECTIONS:
                    nr = row + dr
                    nc = col + dc

                    if in_bounds(nr, nc, size) and board[nr][nc] == Board.EMPTY:
                        potential_squares.add((nr, nc))

    return len(potential_squares) # quantas jogadas eu talvez tenha no futuro, baseado em quantas casas vazias estão próximas a peças do adversário

# board tabuleiro, jogador player, adversario --> int peças no canto de jogador - de adversário
def corner_score(board, player: str, adversary: str) -> int:
    size = len(board)

    corners = [
        (0, 0),
        (0, size - 1),
        (size - 1, 0),
        (size - 1, size - 1),
    ]

    player_corners = 0
    adversary_corners = 0

    for row, col in corners:
        if board[row][col] == player:
            player_corners += 1
        elif board[row][col] == adversary:
            adversary_corners += 1

    return player_corners - adversary_corners

def corner_danger_score(board, player: str, adversary: str) -> int:
    """
    Penaliza peças próximas a cantos vazios.
    Se o canto está vazio, casas adjacentes a ele são perigosas.
    """

    size = len(board)

    danger_map = {
        (0, 0): [(0, 1), (1, 0), (1, 1)],
        (0, size - 1): [(0, size - 2), (1, size - 1), (1, size - 2)],
        (size - 1, 0): [(size - 2, 0), (size - 1, 1), (size - 2, 1)],
        (size - 1, size - 1): [
            (size - 2, size - 1),
            (size - 1, size - 2),
            (size - 2, size - 2),
        ],
    } # mapeia cada canto para as casas adjacentes a ele que são perigosas se o canto estiver vazio

    my_danger = 0
    adversary_danger = 0

    for corner, adjacent_squares in danger_map.items():
        corner_row, corner_col = corner

        if board[corner_row][corner_col] != Board.EMPTY:
            continue

        for row, col in adjacent_squares:
            if board[row][col] == player:
                my_danger += 1
            elif board[row][col] == adversary:
                adversary_danger += 1

    return my_danger - adversary_danger



def line_control_score(board, player: str, adversary: str) -> float:
    """
    linhas, colunas ou diagonais com peças de uma só cor e vazios
    recebem pequena pontuação porque indicam controle de parte do tabuleiro e potencial para formar linhas/colunas/diagonais fortes no futuro
    corre risco pois adversário pode colocar peça para bloquear, mas ainda assim é melhor do que ter peças misturadas com as do adversário
    
    """

    score = 0.0

    for line in get_lines(board):
        player_count = line.count(player)
        adversary_count = line.count(adversary)

        if player_count > 0 and adversary_count == 0:
            score += player_count
        elif adversary_count > 0 and player_count == 0:
            score -= adversary_count

    return score

# state Tabuleiro Preenchido, player Jogador --> float Valor heurístico para o estado
def evaluate_custom(state, player: str) -> float:
    """
    Heurística customizada para Othello.

    Combina:
    - diferença de peças;
    - valor posicional;
    - mobilidade;
    - mobilidade potencial;
    - controle de cantos;
    - perigo perto dos cantos;
    - peças de fronteira;
    - estabilidade aproximada em bordas;
    - controle simples de linhas/colunas/diagonais.
    """

    adversary = opponent(player)

    if state.is_terminal(): # primeiro verifica se o estado é terminal, porque nesse caso a heurística deve refletir vitória, derrota ou empate, independentemente dos outros fatores
        winner = state.winner()

        if winner == player:
            return 100000.0
        elif winner == adversary:
            return -100000.0
        else:
            return 0.0

    board = get_board_matrix(state)
    player_count, adversary_count, empty_count = count_pieces(state, player, adversary)
    piece_diff = player_count - adversary_count

    pos_score = positional_score(board, player, adversary)

    mob_score = mobility_score(state, player, adversary)

    player_potential = potential_mobility(board, player, adversary)
    adversary_potential = potential_mobility(board, adversary, player)
    potential_score = player_potential - adversary_potential

    corners = corner_score(board, player, adversary)

    danger = corner_danger_score(board, player, adversary)

    my_frontier = frontier_discs(board, player)
    adversary_frontier = frontier_discs(board, adversary)
    frontier_score = adversary_frontier - my_frontier  # menos (my)frontier disks = melhor, porque são casas vulneráveis

    my_stable = stable_edge_discs_from_corners(board, player)
    adversary_stable = stable_edge_discs_from_corners(board, adversary)
    stable_score = my_stable - adversary_stable  # menos frontier 

    line_score = line_control_score(board, player, adversary)

    # A diferença de peças é mais importante no final --> usar peso dinâmico de peças
    if empty_count > 20:  #inicio do jogo
        piece_weight = 0.5
    elif empty_count > 10:  #meio do jogo
        piece_weight = 2.0
    else:                   #final do jogo --> mais pesopara dif de peças
        piece_weight = 6.0

    score = (
        piece_weight * piece_diff
        + 1.0 * pos_score
        + 8.0 * mob_score
        + 3.0 * potential_score
        + 30.0 * corners
        - 12.0 * danger
        + 4.0 * frontier_score
        + 10.0 * stable_score
        + 0.5 * line_score
    )

    return float(score)