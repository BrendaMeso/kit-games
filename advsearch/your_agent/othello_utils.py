from ..othello.board import Board 

# funções reutilizáveis - operações genéricas sobre estados/tabuleiros de Othello 
# métrica é algo observável do estado atual  do jogo
# heurística é como combinar métricas para avaliar/estimar qualidade do estado

DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
] # 8 direções ao redor de uma casa --> serve para "olhar" vizinhos

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

# estado atual state, jogador player --> int movimentos válidos para jogador 
def legal_moves_count_for(state, player: str) -> int:
    temp_state = state.copy()
    temp_state.player = player

    return len(temp_state.legal_moves())
       
# player atual --> opponent     // é adversário do jogador atual
def opponent(player: str) -> str:
    return Board.opponent(player)


# state --> matriz 8x8 (domínio: 'B', 'W', '.')     // é tabuleiro atual 
def get_board_matrix(state):
    return state.get_board().tiles


# posição no tabuleiro (row, col) --> valor booleano  // se posição está dentro de matriz side x side (é válida)
def in_bounds(row: int, col: int, size: int) -> bool:
    return 0 <= row < size and 0 <= col < size


# tabuleiro board, jogador player --> int peças de jogador com pelo menos uma casa vazia adjacente (Ex: "B .B" conta 2 peças de B, mas "BWB" conta 0 peças de B)
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
                nr = row + dr  # nr é a linha vizinha
                nc = col + dc   # nc é a coluna vizinha

                if in_bounds(nr, nc, size) and board[nr][nc] == Board.EMPTY:
                    count += 1
                    break

    return count

# tabuleiro board, jogador player, adversário --> int peças contínuas de jogador em bordas a partir de cantos ocupados (Ex: se canto (0, 0) é do jogador, e (0, 1) e (0, 2) também são, conta 3 peças estáveis; se (0, 1) é vazio ou do adversário, conta só 1 peça estável)
def stable_edge_discs_from_corners(board, player: str) -> int:
    """
    Aproxima estabilidade:
    se um canto pertence ao jogador,
    então peças contínuas dele nas bordas próximas
    provavelmente também são estáveis
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

# tabuleiro board --> list[list] sequências horizontais, verticais e diagonais do tabuleiro
def get_lines(board):
    """
    Retorna linhas, colunas e diagonais principais do tabuleiro.
    transforma um tabuleiro em várias "sequencias analisaveis"
    então reorganiza o tabuleiro em sequências lineares = percorre o tabuleiro em 4 direções
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