from typing import Tuple

from .mcts import make_move as mcts_move


def make_move(state) -> Tuple[int, int]:
    """
    Agente de Othello usando MCTS genérico.
    """

    return mcts_move(state)