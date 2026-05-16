import random
import time
from typing import Tuple
from ..othello.gamestate import GameState
from ..othello.board import Board
from .minimax import minimax_move
import csv

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


DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
] # 8 direções ao redor de uma casa --> serve para "olhar" vizinhos


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

# player atual --> opponent     // é adversário do jogador atual
def opponent(player: str) -> str:
    if player == Board.BLACK:
        return Board.WHITE
    return Board.BLACK

# state --> matriz 8x8 (domínio: 'B', 'W', '.')     // é tabuleiro atual 
def get_board_matrix(state):
    return state.get_board().tiles

# posição no tabuleiro (row, col) --> valor booleano  // se posição está dentro de matriz side x side (é válida)
def in_bounds(row: int, col: int, size: int) -> bool:
    return 0 <= row < size and 0 <= col < size

# métricas auxiliares para avaliação heurística

# tabuleiro board, jogador player, adversário --> (int peças jogador, int peças adversário, int espaços vazios)
def count_pieces(state, player: str, adversary: str) -> tuple[int, int, int]:
    """
    Conta peças usando os contadores internos do Board.
    Essa versão evita percorrer o tabuleiro inteiro.
    """

    board = state.get_board()

    player_count = board.num_pieces(player)
    adversary_count = board.num_pieces(adversary)
    empty_count = board.num_pieces(Board.EMPTY)

    return player_count, adversary_count, empty_count


def positional_score(board, player: str, adversary: str) -> float:
    score = 0.0

    for row in range(8):
        for col in range(8):
            cell = board[row][col]

            if cell == player:
                score += EVAL_TEMPLATE[row][col]
            elif cell == adversary:
                score -= EVAL_TEMPLATE[row][col]

    return score


def legal_moves_count_for(state, player: str) -> int:
    """
    Conta jogadas legais para um jogador.
    Usa cópia do estado para não alterar o estado original.
    """

    if hasattr(state, "copy"):
        temp_state = state.copy()
        temp_state.player = player
        return len(temp_state.legal_moves())
# Copio o estado atual, altero o jogador apenas na cópia e calculo as jogadas legais dessa cópia.

    original_player = state.player

    try:
        state.player = player
        return len(state.legal_moves())
    finally:
        state.player = original_player

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
    }

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


def frontier_discs(board, player: str) -> int:
    """
    Conta peças do jogador adjacentes a casas vazias.
    Peças de fronteira costumam ser vulneráveis.
    """

    size = len(board)
    count = 0

    for row in range(size):
        for col in range(size):
            if board[row][col] != player:
                continue

            for dr, dc in DIRECTIONS:
                nr = row + dr
                nc = col + dc

                if in_bounds(nr, nc, size) and board[nr][nc] == Board.EMPTY:
                    count += 1
                    break

    return count


def stable_edge_discs_from_corners(board, player: str) -> int:
    """
    Aproxima estabilidade:
    conta peças contínuas do jogador a partir de cantos ocupados por ele.
    """

    size = len(board)
    stable = set()

    corner_directions = {
        (0, 0): [(0, 1), (1, 0)],
        (0, size - 1): [(0, -1), (1, 0)],
        (size - 1, 0): [(0, 1), (-1, 0)],
        (size - 1, size - 1): [(0, -1), (-1, 0)],
    }

    for corner, directions in corner_directions.items():
        row, col = corner

        if board[row][col] != player:
            continue

        stable.add((row, col))

        for dr, dc in directions:
            nr = row + dr
            nc = col + dc

            while in_bounds(nr, nc, size) and board[nr][nc] == player:
                stable.add((nr, nc))
                nr += dr
                nc += dc

    return len(stable)


def get_lines(board):
    """
    Retorna linhas, colunas e diagonais principais do tabuleiro.
    Essa função é usada para uma métrica leve de controle estrutural.
    """

    size = len(board)
    lines = []

    # linhas
    for row in range(size):
        lines.append([board[row][col] for col in range(size)])

    # colunas
    for col in range(size):
        lines.append([board[row][col] for row in range(size)])

    # diagonais
    for start_col in range(size):
        diagonal = []
        row = 0
        col = start_col

        while row < size and col < size:
            diagonal.append(board[row][col])
            row += 1
            col += 1

        if len(diagonal) >= 4:
            lines.append(diagonal)

    for start_row in range(1, size):
        diagonal = []
        row = start_row
        col = 0

        while row < size and col < size:
            diagonal.append(board[row][col])
            row += 1
            col += 1

        if len(diagonal) >= 4:
            lines.append(diagonal)

    # diagonais invertidas
    for start_col in range(size):
        diagonal = []
        row = 0
        col = start_col

        while row < size and col >= 0:
            diagonal.append(board[row][col])
            row += 1
            col -= 1

        if len(diagonal) >= 4:
            lines.append(diagonal)

    for start_row in range(1, size):
        diagonal = []
        row = start_row
        col = size - 1

        while row < size and col >= 0:
            diagonal.append(board[row][col])
            row += 1
            col -= 1

        if len(diagonal) >= 4:
            lines.append(diagonal)

    return lines


def line_control_score(board, player: str, adversary: str) -> float:
    """
    Métrica inspirada na sua ideia:
    linhas, colunas ou diagonais com peças de uma só cor e vazios
    recebem pequena pontuação.

    Peso baixo, porque Othello não é jogo da velha.
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

    if state.is_terminal():
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
    frontier_score = adversary_frontier - my_frontier

    my_stable = stable_edge_discs_from_corners(board, player)
    adversary_stable = stable_edge_discs_from_corners(board, adversary)
    stable_score = my_stable - adversary_stable

    line_score = line_control_score(board, player, adversary)

    # A diferença de peças é mais importante no final.
    if empty_count > 20:
        piece_weight = 0.5
    elif empty_count > 10:
        piece_weight = 2.0
    else:
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