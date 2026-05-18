# python test_othello_evaluations.py
# python server.py othello advsearch/your_agent/othello_minimax_mask.py advsearch/randomplayer/agent.py


import random
from typing import Tuple
from ..othello.gamestate import GameState
from ..othello.board import Board
from .minimax import minimax_move

# Voce pode criar funcoes auxiliares neste arquivo
# e tambem modulos auxiliares neste pacote.
#
# Nao esqueca de renomear 'your_agent' com o nome
# do seu agente.

# mask template adjusted from https://web.fe.up.pt/~eol/IA/MIA0203/trabalhos/Damas_Othelo/Docs/Eval.html
# could optimize for symmetries but just put all values here for coding speed :P
# DO NOT CHANGE! 

MAX_DEPTH = 4

EVAL_TEMPLATE = [
    [100, -30, 6, 2, 2, 6, -30, 100],
    [-30, -50, 1, 1, 1, 1, -50, -30],
    [  6,   1, 1, 1, 1, 1,   1,   6],
    [  2,   1, 1, 3, 3, 1,   1,   2],
    [  2,   1, 1, 3, 3, 1,   1,   2],
    [  6,   1, 1, 1, 1, 1,   1,   6],
    [-30, -50, 1, 1, 1, 1, -50, -30],
    [100, -30, 6, 2, 2, 6, -30, 100]
]


def make_move(state) -> Tuple[int, int]:
    """
    Returns a move for the given game state.
    """

    return minimax_move(state, MAX_DEPTH, evaluate_mask)


def evaluate_mask(state, player: str) -> float:

    adversary = Board.opponent(player)

    board = state.get_board().tiles

    score = 0.0

    for row in range(8):
        for col in range(8):

            if board[row][col] == player:
                score += EVAL_TEMPLATE[row][col]

            elif board[row][col] == adversary:
                score -= EVAL_TEMPLATE[row][col]

    return float(score)