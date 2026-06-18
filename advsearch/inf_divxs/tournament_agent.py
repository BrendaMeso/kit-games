import random
from typing import Tuple

from advsearch.inf_divxs import minimax
from ..othello.gamestate import GameState
from ..othello.board import Board
from .othello_minimax_custom import make_move
from advsearch.inf_divxs import othello_minimax_custom

# Voce pode criar funcoes auxiliares neste arquivo
# e tambem modulos auxiliares neste pacote.
#
# Nao esqueca de renomear 'inf_divxs' com o nome
# do seu agente.


def make_move(state) -> Tuple[int, int]:
    """
    Returns a move for the given game state. 
    Consider that this will be called in the Othello tournament situation,
    so you should call the best implementation you got.

    :param state: state to make the move
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """

    return othello_minimax_custom.make_move(state)

    #if state.game_name == 'Othello':
    #    return random.choice([(2, 3), (4, 5), (5, 4), (3, 2)])


