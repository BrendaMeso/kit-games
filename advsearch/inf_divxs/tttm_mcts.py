# py server.py tttm advsearch/randomplayer/agent.py advsearch/inf_divxs/tttm_mcts.py -d 5 -p 0.5

from typing import Tuple
from .mcts import make_move as mcts_move


def make_move(state) -> Tuple[int, int]:
    """
    Agente de Tic-Tac-Toe Misère usando MCTS genérico.
    """

    return mcts_move(state)
