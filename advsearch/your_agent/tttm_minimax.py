import random
from typing import Tuple
from ..tttm.gamestate import GameState
from ..tttm.board import Board
from .minimax import minimax_move

# Voce pode criar funcoes auxiliares neste arquivo
# e tambem modulos auxiliares neste pacote.
# Nao esqueca de renomear 'your_agent' com o nome
# do seu agente.


def make_move(state: GameState) -> Tuple[int, int]:
    """
    Retorna uma jogada calculada pelo algoritmo minimax para o estado de jogo fornecido.
    :param state: estado para fazer a jogada
    :return: tupla (int, int) com as coordenadas x, y da jogada (lembre-se: 0 é a primeira linha/coluna)
    """

    # Use profundidade ilimitada na sua entrega,
    # uma vez que o jogo tem profundidade maxima 9. 
    # Preencha a funcao utility com o valor de um estado terminal e passe-a como funcao de avaliação para seu minimax_move

    return minimax_move(
        state = state,
        max_depth = -1, # profundiade ilimitada
        eval_func = utility
    )



def utility(state, player:str) -> float:
    """
    Retorna a utilidade de um estado (terminal) 
    + 1 = vitoria do jogador
    - 1 = derrota do jogador
      0 = empate
    """

    winner = state.winner()

    # empate 
    if winner is None:
        return 0
    
    # vitoria
    if winner == player:
        return 1
    
    # derrota
    return -1   
