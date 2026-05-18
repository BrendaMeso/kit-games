import random
from typing import Tuple
from ..othello.gamestate import GameState
from ..othello.board import Board
from .minimax import minimax_move

MAX_DEPTH = 4


def make_move(state) -> Tuple[int, int]:
    """
    Returns a move for the given game state.
    """

    return minimax_move(state, MAX_DEPTH, evaluate_count)


def evaluate_count(state, player: str) -> float:

    adversary = Board.opponent(player)

    board = state.get_board()

    player_count = board.num_pieces(player)
    adversary_count = board.num_pieces(adversary)

    return float(player_count - adversary_count)